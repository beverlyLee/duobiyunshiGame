import pygame
import math
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, BLACK, GRAY, YELLOW,
    SKILL_TREE_COLOR,
    SKILL_NODE_RADIUS, SKILL_ROW_SPACING, SKILL_BRANCH_WIDTH
)
from game.core.utils import get_chinese_font, get_font, get_large_font, get_medium_font, get_small_font
from game.core.skill_tree import (
    SkillTreeManager, Skill, SkillBranch, SkillBranchType, SkillType,
    get_skill_tree_manager
)
from game.ui.button import Button


class SkillNodeUI:
    def __init__(self, skill: Skill, branch_type: SkillBranchType, row: int, col: int):
        self.skill = skill
        self.branch_type = branch_type
        self.row = row
        self.col = col
        
        base_x = self._get_branch_base_x(branch_type)
        self.x = base_x
        self.y = 185 + row * 75
        
        self.radius = 22
        self.hovered = False
        self.pressed = False
        self.pulse_phase = 0
        
    def _get_branch_base_x(self, branch_type: SkillBranchType) -> int:
        if branch_type == SkillBranchType.ATTACK:
            return SCREEN_WIDTH // 4
        elif branch_type == SkillBranchType.DEFENSE:
            return SCREEN_WIDTH // 2
        else:
            return SCREEN_WIDTH * 3 // 4
    
    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
    
    def contains_point(self, pos):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return dx * dx + dy * dy <= self.radius * self.radius
    
    def get_node_color(self, manager: SkillTreeManager):
        if not self.skill.unlocked:
            available = manager.can_upgrade_skill(self.skill.type)
            if available:
                return SKILL_TREE_COLOR["AVAILABLE"]
            return SKILL_TREE_COLOR["LOCKED"]
        
        if self.skill.current_level >= self.skill.max_level:
            return SKILL_TREE_COLOR["MAXED"]
        
        return SKILL_TREE_COLOR["UNLOCKED"]
    
    def update(self):
        self.pulse_phase += 0.05
    
    def draw(self, surface, manager: SkillTreeManager, mouse_pos):
        self.hovered = self.contains_point(mouse_pos)
        
        base_color = self.get_node_color(manager)
        
        if self.hovered:
            glow_radius = self.radius + 10
            glow_alpha = 100
            for i in range(3):
                current_glow = glow_radius - i * 4
                current_alpha = int(glow_alpha * (1 - i * 0.3))
                glow_surface = pygame.Surface((current_glow * 2, current_glow * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surface,
                    (*SKILL_TREE_COLOR["HOVER"], current_alpha),
                    (current_glow, current_glow),
                    current_glow
                )
                surface.blit(glow_surface, (self.x - current_glow, self.y - current_glow))
        
        display_radius = self.radius
        if self.hovered:
            display_radius += 3
        elif self.skill.unlocked and self.skill.current_level < self.skill.max_level:
            pulse = 2 * math.sin(self.pulse_phase)
            display_radius += pulse
        
        pygame.draw.circle(surface, (20, 20, 30), (self.x, self.y), display_radius + 2)
        
        pygame.draw.circle(surface, base_color, (self.x, self.y), display_radius)
        
        if self.skill.unlocked:
            inner_color = tuple(min(255, c + 40) for c in base_color)
            pygame.draw.circle(surface, inner_color, (self.x, self.y), display_radius - 5, 2)
        
        level_text = f"{self.skill.current_level}/{self.skill.max_level}"
        
        text_font = get_chinese_font(18)
        text_surf = text_font.render(level_text, True, WHITE)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, text_rect)
        
        name_font = get_chinese_font(14)
        name_surf = name_font.render(self.skill.name, True, (200, 200, 200))
        name_rect = name_surf.get_rect(center=(self.x, self.y + display_radius + 12))
        surface.blit(name_surf, name_rect)
    
    def draw_tooltip(self, surface, manager: SkillTreeManager):
        if not self.hovered:
            return
        
        tooltip_width = 180
        tooltip_padding = 15
        line_spacing = 22
        
        lines = []
        lines.append(self.skill.name)
        lines.append("")
        lines.append(self.skill.description)
        lines.append("")
        
        if self.skill.current_level < self.skill.max_level:
            next_cost = self.skill.get_next_cost()
            if next_cost == 0 or next_cost is None:
                lines.append("状态: 免费解锁")
            else:
                lines.append(f"下一级消耗: {next_cost} 技能点")
                can_upgrade = manager.can_upgrade_skill(self.skill.type)
                if can_upgrade:
                    lines.append("点击升级！")
                else:
                    lines.append("需要前置技能或技能点不足")
        else:
            lines.append("状态: 已满级")
        
        if self.skill.requires:
            from game.core.skill_tree import SKILL_CONFIG
            req_names = []
            for req_type in self.skill.requires:
                for branch_config in SKILL_CONFIG.values():
                    for skill_config in branch_config["skills"]:
                        if skill_config["type"] == req_type:
                            req_names.append(skill_config["name"])
                            break
            if req_names:
                lines.append("")
                lines.append("需要: " + ", ".join(req_names))
        
        title_font = get_chinese_font(22)
        normal_font = get_chinese_font(16)
        
        max_width = 0
        for i, line in enumerate(lines):
            font = title_font if i == 0 else normal_font
            text_width = font.size(line)[0]
            max_width = max(max_width, text_width)
        
        tooltip_width = max(max_width + tooltip_padding * 2, tooltip_width)
        tooltip_height = len(lines) * line_spacing + tooltip_padding * 2
        
        tooltip_x = self.x + self.radius + 20
        tooltip_y = self.y - tooltip_height // 2
        
        if tooltip_x + tooltip_width > SCREEN_WIDTH:
            tooltip_x = self.x - self.radius - 20 - tooltip_width
        if tooltip_y < 20:
            tooltip_y = 20
        if tooltip_y + tooltip_height > SCREEN_HEIGHT - 20:
            tooltip_y = SCREEN_HEIGHT - 20 - tooltip_height
        
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        pygame.draw.rect(
            tooltip_surface,
            (15, 15, 35, 245),
            (0, 0, tooltip_width, tooltip_height),
            border_radius=8
        )
        pygame.draw.rect(
            tooltip_surface,
            (80, 120, 180, 200),
            (0, 0, tooltip_width, tooltip_height),
            2,
            border_radius=8
        )
        
        current_y = tooltip_padding
        for i, line in enumerate(lines):
            font = title_font if i == 0 else normal_font
            color = YELLOW if i == 0 else WHITE
            
            if line:
                text_surf = font.render(line, True, color)
                text_rect = text_surf.get_rect(midtop=(tooltip_width // 2, current_y))
                tooltip_surface.blit(text_surf, text_rect)
            
            current_y += line_spacing
        
        surface.blit(tooltip_surface, (tooltip_x, tooltip_y))


class SkillTreeUI:
    def __init__(self):
        self.manager = get_skill_tree_manager()
        self.nodes = {}
        self.branch_connections = {}
        
        self._create_nodes()
        self._create_connections()
        
        self.back_button = Button(
            20, SCREEN_HEIGHT - 50,
            120, 35, "返回", GRAY, (150, 150, 150)
        )
        
        self.visual_phase = 0
    
    def _create_nodes(self):
        from game.core.skill_tree import SKILL_CONFIG
        
        for branch_type in SkillBranchType:
            branch = self.manager.get_branch(branch_type)
            branch_config = SKILL_CONFIG[branch_type]
            
            for row, skill_config in enumerate(branch_config["skills"]):
                skill_type = skill_config["type"]
                skill = branch.get_skill(skill_type)
                if skill:
                    node = SkillNodeUI(skill, branch_type, row, 0)
                    self.nodes[skill_type] = node
    
    def _create_connections(self):
        from game.core.skill_tree import SKILL_CONFIG
        
        self.branch_connections = {}
        
        for branch_type in SkillBranchType:
            branch_config = SKILL_CONFIG[branch_type]
            connections = []
            
            skill_list = branch_config["skills"]
            for i, skill_config in enumerate(skill_list):
                skill_type = skill_config["type"]
                
                for req_type in skill_config.get("requires", []):
                    from_node = self.nodes.get(req_type)
                    to_node = self.nodes.get(skill_type)
                    
                    if from_node and to_node:
                        connections.append({
                            "from": from_node,
                            "to": to_node,
                            "from_type": req_type,
                            "to_type": skill_type
                        })
            
            self.branch_connections[branch_type] = connections
    
    def get_branch_title_pos(self, branch_type: SkillBranchType):
        if branch_type == SkillBranchType.ATTACK:
            return SCREEN_WIDTH // 4, 110
        elif branch_type == SkillBranchType.DEFENSE:
            return SCREEN_WIDTH // 2, 110
        else:
            return SCREEN_WIDTH * 3 // 4, 110
    
    def _draw_connections(self, surface):
        from game.core.skill_tree import SKILL_CONFIG
        
        for branch_type, connections in self.branch_connections.items():
            branch_config = SKILL_CONFIG[branch_type]
            branch_color = branch_config["color"]
            
            for conn in connections:
                from_node = conn["from"]
                to_node = conn["to"]
                
                from_skill = self.manager.get_skill(conn["from_type"])
                to_skill = self.manager.get_skill(conn["to_type"])
                
                if from_skill and from_skill.unlocked:
                    line_color = branch_color
                    line_width = 3
                else:
                    line_color = SKILL_TREE_COLOR["LOCKED"]
                    line_width = 2
                
                start_y = from_node.y + from_node.radius + 32
                end_y = to_node.y - to_node.radius - 8
                
                pygame.draw.line(
                    surface, line_color,
                    (from_node.x, start_y),
                    (to_node.x, end_y),
                    line_width
                )
                
                if from_skill and from_skill.unlocked:
                    num_dots = 2
                    total_dist = end_y - start_y
                    for i in range(num_dots):
                        dot_progress = (i + 1) / (num_dots + 1)
                        dot_y = start_y + total_dist * dot_progress
                        dot_y += math.sin(self.visual_phase + i * 2) * 4
                        pygame.draw.circle(surface, branch_color, (from_node.x, int(dot_y)), 3)
    
    def update(self):
        self.visual_phase += 0.08
        for node in self.nodes.values():
            node.update()
    
    def handle_click(self, mouse_pos) -> bool:
        if self.back_button.is_clicked(mouse_pos, True):
            return True
        
        for skill_type, node in self.nodes.items():
            if node.contains_point(mouse_pos):
                if self.manager.can_upgrade_skill(skill_type):
                    self.manager.upgrade_skill(skill_type)
                    from game.core.audio_manager import get_audio_manager, SoundType
                    audio = get_audio_manager()
                    audio.play_sound(SoundType.POWERUP)
                break
        
        return False
    
    def draw(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((10, 10, 30))
        surface.blit(overlay, (0, 0))
        
        star_phase = self.visual_phase * 0.5
        for i in range(40):
            star_x = int((i * 137 + math.sin(star_phase + i) * 20) % SCREEN_WIDTH)
            star_y = int((i * 89 + math.cos(star_phase + i * 0.5) * 10) % SCREEN_HEIGHT)
            star_alpha = int(40 + 25 * math.sin(star_phase + i * 0.3))
            pygame.draw.circle(surface, (star_alpha, star_alpha, star_alpha), (star_x, star_y), 1)
        
        title_y = 32
        title_font = get_chinese_font(56)
        title_text = title_font.render("技能树", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        
        glow_alpha = 60 + int(20 * math.sin(self.visual_phase * 0.8))
        for offset in range(3, 0, -1):
            glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            glow_text = title_font.render("技能树", True, YELLOW)
            glow_text.set_alpha(glow_alpha - offset * 15)
            glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH // 2, title_y))
            glow_surf.blit(glow_text, glow_rect)
            surface.blit(glow_surf, (0, 0))
        
        surface.blit(title_text, title_rect)
        
        underline_y = title_y + title_rect.height // 2 + 8
        underline_width = 120
        underline_x = SCREEN_WIDTH // 2 - underline_width // 2
        pygame.draw.rect(surface, YELLOW, (underline_x, underline_y, underline_width, 3))
        
        shadow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (YELLOW[0], YELLOW[1], YELLOW[2], 100), 
                        (underline_x - 20, underline_y + 1, underline_width + 40, 1))
        surface.blit(shadow_surf, (0, 0))
        
        points_y = underline_y + 35
        points_label_font = get_chinese_font(26)
        points_value_font = get_chinese_font(36)
        
        points_label = "可用技能点:"
        points_value = str(self.manager.skill_points)
        
        label_surf = points_label_font.render(points_label, True, (200, 200, 200))
        value_surf = points_value_font.render(points_value, True, YELLOW)
        
        total_width = label_surf.get_width() + value_surf.get_width() + 15
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        
        box_padding = 12
        box_width = total_width + box_padding * 2
        box_height = max(label_surf.get_height(), value_surf.get_height()) + box_padding * 2
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = points_y - box_height // 2
        
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (40, 40, 70, 180), (0, 0, box_width, box_height), border_radius=10)
        pygame.draw.rect(box_surface, (100, 100, 150, 150), (0, 0, box_width, box_height), 2, border_radius=10)
        surface.blit(box_surface, (box_x, box_y))
        
        surface.blit(label_surf, (start_x, points_y - label_surf.get_height() // 2))
        surface.blit(value_surf, (start_x + label_surf.get_width() + 15, points_y - value_surf.get_height() // 2))
        
        from game.core.skill_tree import SKILL_CONFIG
        
        branch_title_y = points_y + 45
        branch_title_font = get_chinese_font(30)
        
        for branch_type in SkillBranchType:
            branch_config = SKILL_CONFIG[branch_type]
            title_x, _ = self.get_branch_title_pos(branch_type)
            
            branch_title = branch_title_font.render(branch_config["name"], True, branch_config["color"])
            branch_title_rect = branch_title.get_rect(center=(title_x, branch_title_y))
            
            title_bg_width = branch_title_rect.width + 30
            title_bg_height = branch_title_rect.height + 10
            title_bg_x = title_x - title_bg_width // 2
            title_bg_y = branch_title_y - title_bg_height // 2
            
            title_bg_surface = pygame.Surface((title_bg_width, title_bg_height), pygame.SRCALPHA)
            bg_color = (*branch_config["color"], 40)
            pygame.draw.rect(title_bg_surface, bg_color, (0, 0, title_bg_width, title_bg_height), border_radius=8)
            surface.blit(title_bg_surface, (title_bg_x, title_bg_y))
            
            surface.blit(branch_title, branch_title_rect)
        
        self._draw_connections(surface)
        
        hovered_node = None
        for node in self.nodes.values():
            node.draw(surface, self.manager, mouse_pos)
            if node.hovered:
                hovered_node = node
        
        if hovered_node:
            hovered_node.draw_tooltip(surface, self.manager)
        
        self.back_button.draw(surface, mouse_pos)
