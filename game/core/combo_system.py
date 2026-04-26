import pygame
import math
from game.config import FPS
from game.core.utils import get_font, get_medium_font, get_large_font

class ComboSystem:
    def __init__(self):
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.combo_timeout = FPS * 2
        
        self.multiplier = 1.0
        self.base_multiplier = 1.0
        
        self.display_combo = 0
        self.display_scale = 1.0
        self.target_scale = 1.0
        self.display_alpha = 255
        
        self.pulse_timer = 0
        self.pulse_speed = 0.15
        
        self.hit_count = 0
        self.total_hits = 0
        
        self.combo_milestones = {
            5: 1.2,
            10: 1.5,
            20: 2.0,
            50: 3.0,
            100: 5.0
        }
    
    def add_hit(self, points=1):
        self.combo += points
        self.hit_count += 1
        self.total_hits += 1
        
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        
        self.combo_timer = self.combo_timeout
        self._update_multiplier()
        
        self.target_scale = 1.3
        self.display_alpha = 255
        
        return self.multiplier
    
    def reset_combo(self):
        if self.combo > 0:
            self.display_scale = 0.5
            self.display_alpha = 100
        
        self.combo = 0
        self.combo_timer = 0
        self.multiplier = self.base_multiplier
        self.hit_count = 0
    
    def _update_multiplier(self):
        self.multiplier = self.base_multiplier
        
        sorted_milestones = sorted(self.combo_milestones.keys())
        for milestone in sorted_milestones:
            if self.combo >= milestone:
                self.multiplier = self.combo_milestones[milestone]
    
    def update(self):
        if self.combo_timer > 0:
            self.combo_timer -= 1
            
            if self.combo_timer <= 0:
                self.reset_combo()
        
        scale_diff = self.target_scale - self.display_scale
        self.display_scale += scale_diff * 0.2
        
        if abs(self.display_scale - self.target_scale) < 0.01:
            self.display_scale = self.target_scale
            self.target_scale = 1.0
        
        if self.combo == 0:
            if self.display_alpha > 50:
                self.display_alpha -= 5
            else:
                self.display_alpha = 0
        
        if self.combo > 0:
            self.pulse_timer += self.pulse_speed
        
        self.display_combo = self.combo
    
    def get_multiplier(self):
        return self.multiplier
    
    def get_combo(self):
        return self.combo
    
    def get_max_combo(self):
        return self.max_combo
    
    def get_total_hits(self):
        return self.total_hits
    
    def draw(self, surface, x, y):
        if self.combo <= 0 and self.display_alpha <= 50:
            return
        
        if self.combo > 0:
            scale = self.display_scale
            alpha = 255
        else:
            scale = self.display_scale
            alpha = self.display_alpha
        
        if self.combo > 0:
            pulse = 0.05 * math.sin(self.pulse_timer)
            scale += pulse
        
        if self.combo >= 100:
            font = get_large_font()
            color = (255, 100, 255)
        elif self.combo >= 50:
            font = get_large_font()
            color = (255, 215, 0)
        elif self.combo >= 20:
            font = get_large_font()
            color = (255, 140, 0)
        elif self.combo >= 10:
            font = get_medium_font()
            color = (255, 100, 100)
        elif self.combo >= 5:
            font = get_medium_font()
            color = (100, 200, 255)
        else:
            font = get_font()
            color = (255, 255, 255)
        
        combo_text = f"{self.combo} 连击"
        text_surface = font.render(combo_text, True, color)
        
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        scaled_width = int(text_width * scale)
        scaled_height = int(text_height * scale)
        
        if scale != 1.0:
            text_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))
        
        draw_x = x - scaled_width // 2
        draw_y = y - scaled_height // 2
        
        if alpha < 255:
            temp_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            temp_surface.blit(text_surface, (0, 0))
            temp_surface.set_alpha(alpha)
            surface.blit(temp_surface, (draw_x, draw_y))
        else:
            surface.blit(text_surface, (draw_x, draw_y))
        
        if self.combo >= 5 and self.multiplier > 1.0:
            multiplier_text = f"x{self.multiplier:.1f}"
            multiplier_font = get_font()
            multiplier_surface = multiplier_font.render(multiplier_text, True, (0, 255, 150))
            
            multiplier_width = multiplier_surface.get_width()
            multiplier_height = multiplier_surface.get_height()
            
            multiplier_x = x - multiplier_width // 2
            multiplier_y = draw_y + scaled_height + 5
            
            surface.blit(multiplier_surface, (multiplier_x, multiplier_y))


class DifficultySystem:
    def __init__(self):
        self.level = 1
        self.score_threshold = 500
        self.level_up_score = 500
        
        self.difficulty_factor = 1.0
        
        self.meteor_speed_multiplier = 1.0
        self.meteor_spawn_multiplier = 1.0
        self.meteor_health_multiplier = 1.0
        
        self.display_level_up = False
        self.level_up_timer = 0
        self.level_up_duration = FPS * 3
        self.just_leveled_up = False
    
    def update(self, current_score):
        self.just_leveled_up = False
        
        if current_score >= self.level_up_score:
            self.level += 1
            self.level_up_score += self.score_threshold * self.level
            self._increase_difficulty()
            self.display_level_up = True
            self.level_up_timer = self.level_up_duration
            self.just_leveled_up = True
        
        if self.display_level_up:
            self.level_up_timer -= 1
            if self.level_up_timer <= 0:
                self.display_level_up = False
    
    def _increase_difficulty(self):
        self.difficulty_factor = 1.0 + (self.level - 1) * 0.1
        
        self.meteor_speed_multiplier = 1.0 + (self.level - 1) * 0.05
        self.meteor_spawn_multiplier = 1.0 + (self.level - 1) * 0.08
        
        if self.level >= 5:
            self.meteor_health_multiplier = 1.2
        if self.level >= 10:
            self.meteor_health_multiplier = 1.5
    
    def get_meteor_speed_multiplier(self):
        return self.meteor_speed_multiplier
    
    def get_meteor_spawn_multiplier(self):
        return self.meteor_spawn_multiplier
    
    def get_meteor_health_multiplier(self):
        return self.meteor_health_multiplier
    
    def get_level(self):
        return self.level
    
    def has_just_leveled_up(self):
        return self.just_leveled_up
    
    def should_display_level_up(self):
        return self.display_level_up
    
    def draw_level_up(self, surface, screen_width, screen_height):
        if not self.display_level_up:
            return
        
        from game.core.utils import get_large_font, get_medium_font
        
        alpha = 255
        if self.level_up_timer < self.level_up_duration // 4:
            alpha = int(255 * (self.level_up_timer / (self.level_up_duration // 4)))
        
        pulse_scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.01)
        
        level_text = f"等级 {self.level}!"
        title_font = get_large_font()
        title_surface = title_font.render(level_text, True, (255, 215, 0))
        
        scaled_width = int(title_surface.get_width() * pulse_scale)
        scaled_height = int(title_surface.get_height() * pulse_scale)
        title_surface = pygame.transform.scale(title_surface, (scaled_width, scaled_height))
        
        title_x = screen_width // 2 - scaled_width // 2
        title_y = screen_height // 2 - scaled_height - 30
        
        if alpha < 255:
            temp_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            temp_surface.blit(title_surface, (0, 0))
            temp_surface.set_alpha(alpha)
            surface.blit(temp_surface, (title_x, title_y))
        else:
            surface.blit(title_surface, (title_x, title_y))
        
        subtitle_text = "难度提升！"
        subtitle_font = get_medium_font()
        subtitle_surface = subtitle_font.render(subtitle_text, True, (255, 100, 100))
        
        subtitle_x = screen_width // 2 - subtitle_surface.get_width() // 2
        subtitle_y = screen_height // 2 + 20
        
        if alpha < 255:
            temp_surface = pygame.Surface((subtitle_surface.get_width(), subtitle_surface.get_height()), pygame.SRCALPHA)
            temp_surface.blit(subtitle_surface, (0, 0))
            temp_surface.set_alpha(alpha)
            surface.blit(temp_surface, (subtitle_x, subtitle_y))
        else:
            surface.blit(subtitle_surface, (subtitle_x, subtitle_y))
