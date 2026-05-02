import pygame
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, BLACK, RED, GREEN, YELLOW, GRAY,
    BLUE, ORANGE, LIGHT_BLUE
)
from game.core.utils import get_font, get_large_font, get_medium_font, get_small_font
from game.core.daily_challenge import (
    DailyChallenge, DailyChallengeManager, get_daily_challenge_manager,
    ModifierType, MODIFIER_CONFIG, RewardType, REWARD_CONFIG, ChallengeRecord
)
from game.ui.button import Button


class UIState(Enum):
    MAIN = "main"
    CHALLENGE_INFO = "challenge_info"
    LEADERBOARD = "leaderboard"
    REWARDS = "rewards"
    HISTORY = "history"


class DailyChallengeUI:
    def __init__(self):
        self.challenge_manager = get_daily_challenge_manager()
        self.current_state = UIState.MAIN
        self.scroll_offset = 0
        self.max_scroll_offset = 0
        
        self._init_buttons()
        
    def _init_buttons(self):
        self.play_challenge_button = Button(
            SCREEN_WIDTH // 2 - 100, 405,
            200, 45, "开始挑战", YELLOW, (200, 180, 0)
        )
        
        self.view_leaderboard_button = Button(
            SCREEN_WIDTH // 2 - 100, 455,
            200, 45, "排行榜", LIGHT_BLUE, (70, 170, 200)
        )
        
        self.view_rewards_button = Button(
            SCREEN_WIDTH // 2 - 100, 505,
            200, 45, "奖励系统", GREEN, (0, 200, 0)
        )
        
        self.view_history_button = Button(
            SCREEN_WIDTH // 2 - 100, 555,
            200, 45, "历史记录", GRAY, (100, 100, 100)
        )
        
        self.back_button = Button(
            50, 50,
            100, 40, "返回", RED, (200, 0, 0)
        )
        
        self.scroll_up_button = Button(
            SCREEN_WIDTH - 60, 80,
            40, 40, "▲", LIGHT_BLUE, (70, 170, 200)
        )
        
        self.scroll_down_button = Button(
            SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60,
            40, 40, "▼", LIGHT_BLUE, (70, 170, 200)
        )
    
    def set_state(self, state: UIState):
        self.current_state = state
        self.scroll_offset = 0
        self._update_scroll_limits()
    
    def _update_scroll_limits(self):
        if self.current_state == UIState.LEADERBOARD:
            records = self.challenge_manager.get_history_records(limit=100)
            item_height = 60
            visible_items = 8
            total_height = len(records) * item_height
            self.max_scroll_offset = max(0, total_height - visible_items * item_height)
        elif self.current_state == UIState.HISTORY:
            records = self.challenge_manager.get_history_records(limit=100)
            item_height = 70
            visible_items = 7
            total_height = len(records) * item_height
            self.max_scroll_offset = max(0, total_height - visible_items * item_height)
        else:
            self.max_scroll_offset = 0
    
    def handle_click(self, mouse_pos: tuple, mouse_clicked: bool) -> Optional[str]:
        if not mouse_clicked:
            return None
        
        if self.current_state == UIState.MAIN:
            if self.play_challenge_button.is_clicked(mouse_pos, mouse_clicked):
                return "play_challenge"
            elif self.view_leaderboard_button.is_clicked(mouse_pos, mouse_clicked):
                self.set_state(UIState.LEADERBOARD)
                return None
            elif self.view_rewards_button.is_clicked(mouse_pos, mouse_clicked):
                self.set_state(UIState.REWARDS)
                return None
            elif self.view_history_button.is_clicked(mouse_pos, mouse_clicked):
                self.set_state(UIState.HISTORY)
                return None
        
        else:
            if self.back_button.is_clicked(mouse_pos, mouse_clicked):
                self.set_state(UIState.MAIN)
                return None
            
            if self.current_state in [UIState.LEADERBOARD, UIState.HISTORY]:
                if self.scroll_up_button.is_clicked(mouse_pos, mouse_clicked):
                    self.scroll_offset = max(0, self.scroll_offset - 60)
                    return None
                elif self.scroll_down_button.is_clicked(mouse_pos, mouse_clicked):
                    self.scroll_offset = min(self.max_scroll_offset, self.scroll_offset + 60)
                    return None
        
        return None
    
    def update(self):
        self.challenge_manager = get_daily_challenge_manager()
    
    def draw(self, surface: pygame.Surface, mouse_pos: tuple):
        if self.current_state == UIState.MAIN:
            self._draw_main_screen(surface, mouse_pos)
        elif self.current_state == UIState.CHALLENGE_INFO:
            self._draw_challenge_info(surface, mouse_pos)
        elif self.current_state == UIState.LEADERBOARD:
            self._draw_leaderboard(surface, mouse_pos)
        elif self.current_state == UIState.REWARDS:
            self._draw_rewards(surface, mouse_pos)
        elif self.current_state == UIState.HISTORY:
            self._draw_history(surface, mouse_pos)
    
    def _draw_main_screen(self, surface: pygame.Surface, mouse_pos: tuple):
        surface.fill(BLACK)
        
        title_text = get_large_font().render("每日挑战", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        surface.blit(title_text, title_rect)
        
        today_challenge = self.challenge_manager.get_current_challenge()
        
        self._draw_modifiers_preview(surface, today_challenge)
        
        date_text = get_font().render(f"日期: {today_challenge.date_str}", True, WHITE)
        date_rect = date_text.get_rect(center=(SCREEN_WIDTH // 2, 290))
        surface.blit(date_text, date_rect)
        
        stars_text = get_medium_font().render(f"累计星星: {self.challenge_manager.total_stars} ⭐", True, (255, 215, 0))
        stars_rect = stars_text.get_rect(center=(SCREEN_WIDTH // 2, 340))
        surface.blit(stars_text, stars_rect)
        
        today_record = self.challenge_manager.get_today_record()
        if today_record:
            completed_text = get_font().render(f"今日已完成! 最高分: {today_record.score} 星星: {today_record.stars}", True, GREEN)
        else:
            completed_text = get_font().render("今日挑战未完成", True, (200, 200, 200))
        completed_rect = completed_text.get_rect(center=(SCREEN_WIDTH // 2, 385))
        surface.blit(completed_text, completed_rect)
        
        self.play_challenge_button.draw(surface, mouse_pos)
        self.view_leaderboard_button.draw(surface, mouse_pos)
        self.view_rewards_button.draw(surface, mouse_pos)
        self.view_history_button.draw(surface, mouse_pos)
    
    def _draw_modifiers_preview(self, surface: pygame.Surface, challenge: DailyChallenge):
        modifier_configs = challenge.get_modifier_configs()
        start_y = 120
        
        for i, modifier in enumerate(modifier_configs):
            x = SCREEN_WIDTH // 2 - 150
            y = start_y + i * 50
            width = 300
            height = 45
            
            bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            bg_surface.fill((*modifier["color"], 80))
            pygame.draw.rect(bg_surface, (*modifier["color"], 200), (0, 0, width, height), 2)
            surface.blit(bg_surface, (x, y))
            
            icon_text = get_font().render(modifier["icon"], True, WHITE)
            icon_rect = icon_text.get_rect(midleft=(x + 20, y + height // 2))
            surface.blit(icon_text, icon_rect)
            
            name_text = get_font().render(modifier["name"], True, WHITE)
            name_rect = name_text.get_rect(midleft=(x + 60, y + height // 2))
            surface.blit(name_text, name_rect)
    
    def _draw_challenge_info(self, surface: pygame.Surface, mouse_pos: tuple):
        surface.fill(BLACK)
        
        title_text = get_large_font().render("挑战详情", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_text, title_rect)
        
        today_challenge = self.challenge_manager.get_current_challenge()
        
        date_text = get_medium_font().render(f"日期: {today_challenge.date_str}", True, WHITE)
        date_rect = date_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        surface.blit(date_text, date_rect)
        
        modifier_title = get_font().render("挑战修改器:", True, LIGHT_BLUE)
        modifier_title_rect = modifier_title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(modifier_title, modifier_title_rect)
        
        modifier_configs = today_challenge.get_modifier_configs()
        start_y = 240
        
        for i, modifier in enumerate(modifier_configs):
            x = SCREEN_WIDTH // 2 - 200
            y = start_y + i * 80
            width = 400
            height = 70
            
            bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            bg_surface.fill((*modifier["color"], 60))
            pygame.draw.rect(bg_surface, (*modifier["color"], 180), (0, 0, width, height), 3)
            surface.blit(bg_surface, (x, y))
            
            icon_text = get_large_font().render(modifier["icon"], True, WHITE)
            icon_rect = icon_text.get_rect(midleft=(x + 30, y + height // 2))
            surface.blit(icon_text, icon_rect)
            
            name_text = get_medium_font().render(modifier["name"], True, WHITE)
            name_rect = name_text.get_rect(topleft=(x + 100, y + 10))
            surface.blit(name_text, name_rect)
            
            desc_text = get_small_font().render(modifier["description"], True, (200, 200, 200))
            desc_rect = desc_text.get_rect(topleft=(x + 100, y + 40))
            surface.blit(desc_text, desc_rect)
        
        self.back_button.draw(surface, mouse_pos)
    
    def _draw_leaderboard(self, surface: pygame.Surface, mouse_pos: tuple):
        surface.fill(BLACK)
        
        title_text = get_large_font().render("排行榜", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        surface.blit(title_text, title_rect)
        
        stats_text = get_font().render(
            f"总挑战次数: {self.challenge_manager.get_total_completions()}  "
            f"最佳分数: {self.challenge_manager.get_best_score()}  "
            f"平均星星: {self.challenge_manager.get_average_stars():.1f}",
            True, WHITE
        )
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
        surface.blit(stats_text, stats_rect)
        
        records = self.challenge_manager.get_history_records(limit=100)
        
        if not records:
            no_record_text = get_font().render("暂无挑战记录", True, GRAY)
            no_record_rect = no_record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(no_record_text, no_record_rect)
        else:
            header_y = 180
            header_bg = pygame.Surface((SCREEN_WIDTH - 100, 40), pygame.SRCALPHA)
            header_bg.fill((100, 100, 100, 100))
            surface.blit(header_bg, (50, header_y))
            
            rank_header = get_font().render("排名", True, YELLOW)
            surface.blit(rank_header, (70, header_y + 8))
            
            date_header = get_font().render("日期", True, YELLOW)
            surface.blit(date_header, (170, header_y + 8))
            
            score_header = get_font().render("分数", True, YELLOW)
            surface.blit(score_header, (350, header_y + 8))
            
            stars_header = get_font().render("星星", True, YELLOW)
            surface.blit(stars_header, (500, header_y + 8))
            
            first_header = get_font().render("首次完成", True, YELLOW)
            surface.blit(first_header, (620, header_y + 8))
            
            start_y = header_y + 45
            
            sorted_records = sorted(records, key=lambda r: r.score, reverse=True)
            
            visible_start = self.scroll_offset // 60
            visible_end = min(visible_start + 8, len(sorted_records))
            
            for i in range(visible_start, visible_end):
                record = sorted_records[i]
                display_i = i - visible_start
                y = start_y + display_i * 60
                
                if display_i % 2 == 0:
                    row_bg = pygame.Surface((SCREEN_WIDTH - 100, 55), pygame.SRCALPHA)
                    row_bg.fill((50, 50, 50, 80))
                    surface.blit(row_bg, (50, y))
                
                rank = i + 1
                
                if rank == 1:
                    rank_color = (255, 215, 0)
                    rank_icon = "🥇"
                elif rank == 2:
                    rank_color = (192, 192, 192)
                    rank_icon = "🥈"
                elif rank == 3:
                    rank_color = (205, 127, 50)
                    rank_icon = "🥉"
                else:
                    rank_color = WHITE
                    rank_icon = f"{rank}"
                
                rank_text = get_font().render(rank_icon, True, rank_color)
                surface.blit(rank_text, (70, y + 12))
                
                date_text = get_font().render(record.date_str, True, WHITE)
                surface.blit(date_text, (170, y + 12))
                
                score_text = get_font().render(f"{record.score}", True, WHITE)
                surface.blit(score_text, (350, y + 12))
                
                stars_display = "⭐" * record.stars
                stars_text = get_font().render(stars_display, True, (255, 215, 0))
                surface.blit(stars_text, (500, y + 12))
                
                first_text = get_font().render("✓" if record.is_first_completion else "-", 
                                               True, GREEN if record.is_first_completion else GRAY)
                surface.blit(first_text, (650, y + 12))
            
            if self.max_scroll_offset > 0:
                self.scroll_up_button.draw(surface, mouse_pos)
                self.scroll_down_button.draw(surface, mouse_pos)
                
                scrollbar_height = SCREEN_HEIGHT - 200
                scrollbar_x = SCREEN_WIDTH - 55
                scrollbar_y = 100
                
                pygame.draw.rect(surface, (50, 50, 50), (scrollbar_x, scrollbar_y, 30, scrollbar_height), 2)
                
                if self.max_scroll_offset > 0:
                    thumb_height = max(40, scrollbar_height * (8 / len(sorted_records)))
                    thumb_y = scrollbar_y + (self.scroll_offset / self.max_scroll_offset) * (scrollbar_height - thumb_height)
                    pygame.draw.rect(surface, LIGHT_BLUE, (scrollbar_x + 2, thumb_y, 26, thumb_height))
        
        self.back_button.draw(surface, mouse_pos)
    
    def _draw_rewards(self, surface: pygame.Surface, mouse_pos: tuple):
        surface.fill(BLACK)
        
        title_text = get_large_font().render("奖励系统", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        surface.blit(title_text, title_rect)
        
        stars_text = get_medium_font().render(f"累计星星: {self.challenge_manager.total_stars} ⭐", True, (255, 215, 0))
        stars_rect = stars_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
        surface.blit(stars_text, stars_rect)
        
        rewards = self.challenge_manager.get_available_rewards()
        
        start_y = 190
        
        for i, reward in enumerate(rewards):
            x = SCREEN_WIDTH // 2 - 320
            y = start_y + i * 130
            width = 640
            height = 120
            
            if reward["unlocked"]:
                bg_color = (0, 150, 0, 80)
                border_color = (0, 200, 0, 200)
            else:
                bg_color = (100, 100, 100, 60)
                border_color = (150, 150, 150, 180)
            
            bg_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            bg_surface.fill(bg_color)
            pygame.draw.rect(bg_surface, border_color, (0, 0, width, height), 3)
            surface.blit(bg_surface, (x, y))
            
            icon_text = get_large_font().render(reward["icon"], True, WHITE)
            icon_rect = icon_text.get_rect(midleft=(x + 40, y + height // 2))
            surface.blit(icon_text, icon_rect)
            
            name_text = get_medium_font().render(reward["name"], True, WHITE)
            name_rect = name_text.get_rect(topleft=(x + 120, y + 20))
            surface.blit(name_text, name_rect)
            
            desc_text = get_small_font().render(reward["description"], True, (200, 200, 200))
            desc_rect = desc_text.get_rect(topleft=(x + 120, y + 70))
            surface.blit(desc_text, desc_rect)
            
            requirement_text = get_font().render(
                f"需要: {reward['required_stars']} 星",
                True, (255, 215, 0) if reward["unlocked"] else GRAY
            )
            requirement_rect = requirement_text.get_rect(topright=(x + width - 40, y + 20))
            surface.blit(requirement_text, requirement_rect)
            
            if reward["unlocked"]:
                status_text = get_font().render("已解锁 ✓", True, GREEN)
                status_rect = status_text.get_rect(topright=(x + width - 40, y + 70))
                surface.blit(status_text, status_rect)
            else:
                progress_text = get_font().render(
                    f"进度: {int(reward['progress'] * 100)}%",
                    True, ORANGE
                )
                progress_rect = progress_text.get_rect(topright=(x + width - 40, y + 65))
                surface.blit(progress_text, progress_rect)
                
                progress_width = 160
                progress_height = 14
                progress_x = x + width - 40 - progress_width
                progress_y = y + 95
                
                pygame.draw.rect(surface, (50, 50, 50), (progress_x, progress_y, progress_width, progress_height))
                
                filled_width = int(progress_width * reward["progress"])
                if filled_width > 0:
                    pygame.draw.rect(surface, ORANGE, (progress_x, progress_y, filled_width, progress_height))
        
        self.back_button.draw(surface, mouse_pos)
    
    def _draw_history(self, surface: pygame.Surface, mouse_pos: tuple):
        surface.fill(BLACK)
        
        title_text = get_large_font().render("历史记录", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        surface.blit(title_text, title_rect)
        
        records = self.challenge_manager.get_history_records(limit=100)
        
        if not records:
            no_record_text = get_font().render("暂无挑战记录", True, GRAY)
            no_record_rect = no_record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(no_record_text, no_record_rect)
        else:
            header_y = 100
            header_bg = pygame.Surface((SCREEN_WIDTH - 100, 40), pygame.SRCALPHA)
            header_bg.fill((100, 100, 100, 100))
            surface.blit(header_bg, (50, header_y))
            
            date_header = get_font().render("日期", True, YELLOW)
            surface.blit(date_header, (70, header_y + 8))
            
            score_header = get_font().render("分数", True, YELLOW)
            surface.blit(score_header, (220, header_y + 8))
            
            stars_header = get_font().render("星星", True, YELLOW)
            surface.blit(stars_header, (370, header_y + 8))
            
            first_header = get_font().render("首次完成", True, YELLOW)
            surface.blit(first_header, (500, header_y + 8))
            
            modifiers_header = get_font().render("修改器", True, YELLOW)
            surface.blit(modifiers_header, (620, header_y + 8))
            
            start_y = header_y + 45
            
            visible_start = self.scroll_offset // 70
            visible_end = min(visible_start + 7, len(records))
            
            for i in range(visible_start, visible_end):
                record = records[i]
                display_i = i - visible_start
                y = start_y + display_i * 70
                
                if display_i % 2 == 0:
                    row_bg = pygame.Surface((SCREEN_WIDTH - 100, 65), pygame.SRCALPHA)
                    row_bg.fill((50, 50, 50, 80))
                    surface.blit(row_bg, (50, y))
                
                date_text = get_font().render(record.date_str, True, WHITE)
                surface.blit(date_text, (70, y + 18))
                
                score_text = get_font().render(f"{record.score}", True, WHITE)
                surface.blit(score_text, (220, y + 18))
                
                stars_display = "⭐" * record.stars
                stars_text = get_font().render(stars_display, True, (255, 215, 0))
                surface.blit(stars_text, (370, y + 18))
                
                first_text = get_font().render("✓" if record.is_first_completion else "-", 
                                               True, GREEN if record.is_first_completion else GRAY)
                surface.blit(first_text, (520, y + 18))
                
                time_text = get_small_font().render(
                    record.completed_at.strftime("%H:%M:%S") if record.completed_at else "-",
                    True, GRAY
                )
                surface.blit(time_text, (70, y + 42))
            
            if self.max_scroll_offset > 0:
                self.scroll_up_button.draw(surface, mouse_pos)
                self.scroll_down_button.draw(surface, mouse_pos)
        
        self.back_button.draw(surface, mouse_pos)


_daily_challenge_ui_instance: Optional[DailyChallengeUI] = None


def get_daily_challenge_ui() -> DailyChallengeUI:
    global _daily_challenge_ui_instance
    if _daily_challenge_ui_instance is None:
        _daily_challenge_ui_instance = DailyChallengeUI()
    return _daily_challenge_ui_instance
