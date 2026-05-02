import pygame
import math
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    POST_PROCESS_CONFIG,
    EXPLOSION_RED, EXPLOSION_DARK_RED,
    ULTIMATE_GOLD, ULTIMATE_LIGHT_GOLD
)


class MotionBlur:
    def __init__(self):
        config = POST_PROCESS_CONFIG["motion_blur"]
        self.enabled = config["enabled"]
        self.speed_threshold = config["speed_threshold"]
        self.intensity = config["intensity"]
        
        self.prev_positions = []
        self.max_history = 5
        self.blur_surface = None
        self.current_intensity = 0.0
        self.target_intensity = 0.0
    
    def update(self, current_position, speed):
        if not self.enabled:
            return
        
        self.prev_positions.append(current_position)
        if len(self.prev_positions) > self.max_history:
            self.prev_positions.pop(0)
        
        if speed >= self.speed_threshold:
            speed_ratio = min(1.0, (speed - self.speed_threshold) / 10.0)
            self.target_intensity = self.intensity * speed_ratio
        else:
            self.target_intensity = 0.0
        
        self.current_intensity += (self.target_intensity - self.current_intensity) * 0.1
    
    def draw(self, surface):
        if not self.enabled or self.current_intensity <= 0.01:
            return
        
        if len(self.prev_positions) < 2:
            return
        
        blur_alpha = int(20 * self.current_intensity)
        
        for i, pos in enumerate(self.prev_positions[:-1]):
            next_pos = self.prev_positions[i + 1]
            alpha = blur_alpha * (i + 1) / len(self.prev_positions)
            
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            temp_surface.set_alpha(int(alpha))
            
            offset_x = int((next_pos[0] - pos[0]) * 0.3)
            offset_y = int((next_pos[1] - pos[1]) * 0.3)
            
            temp_surface.blit(surface, (offset_x, offset_y))
            surface.blit(temp_surface, (0, 0))


class ColorBoost:
    def __init__(self):
        config = POST_PROCESS_CONFIG["color_boost"]
        self.enabled = config["enabled"]
        self.saturation_base = config["saturation_base"]
        self.saturation_high_combo = config["saturation_high_combo"]
        self.combo_threshold = config["combo_threshold"]
        
        self.current_saturation = self.saturation_base
        self.target_saturation = self.saturation_base
    
    def update(self, combo_count):
        if not self.enabled:
            return
        
        if combo_count >= self.combo_threshold:
            combo_ratio = min(1.0, (combo_count - self.combo_threshold) / 30.0)
            self.target_saturation = self.saturation_base + combo_ratio * (self.saturation_high_combo - self.saturation_base)
        else:
            self.target_saturation = self.saturation_base
        
        self.current_saturation += (self.target_saturation - self.current_saturation) * 0.05
    
    def apply(self, surface):
        if not self.enabled:
            return surface
        
        if abs(self.current_saturation - self.saturation_base) < 0.01:
            return surface
        
        saturation_factor = self.current_saturation
        
        if saturation_factor == 1.0:
            return surface
        
        temp_surface = surface.copy()
        pixels = pygame.PixelArray(temp_surface)
        
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                color = temp_surface.unmap_rgb(pixels[x, y])
                
                r = color.r
                g = color.g
                b = color.b
                
                gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
                
                r = int(gray + saturation_factor * (r - gray))
                g = int(gray + saturation_factor * (g - gray))
                b = int(gray + saturation_factor * (b - gray))
                
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                pixels[x, y] = temp_surface.map_rgb((r, g, b))
        
        del pixels
        return temp_surface


class DangerFlash:
    def __init__(self):
        config = POST_PROCESS_CONFIG["danger_flash"]
        self.enabled = config["enabled"]
        self.low_hp_threshold = config["low_hp_threshold"]
        self.flash_interval = config["flash_interval"]
        self.red_tint_alpha = config["red_tint_alpha"]
        
        self.is_active = False
        self.flash_timer = 0
        self.flash_phase = 0
        
        self.danger_surface = None
        self._create_danger_surface()
    
    def _create_danger_surface(self):
        self.danger_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        max_dist = math.sqrt(center_x * center_x + center_y * center_y)
        
        for x in range(0, SCREEN_WIDTH, 5):
            for y in range(0, SCREEN_HEIGHT, 5):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                dist_ratio = dist / max_dist
                
                edge_intensity = 1.0 - dist_ratio
                if edge_intensity > 0.5:
                    alpha = int(self.red_tint_alpha * edge_intensity)
                    temp_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
                    pygame.draw.circle(
                        temp_surface,
                        (EXPLOSION_RED[0], EXPLOSION_RED[1], EXPLOSION_RED[2], alpha),
                        (5, 5),
                        5
                    )
                    self.danger_surface.blit(temp_surface, (x, y))
        
        for x in range(SCREEN_WIDTH):
            alpha = int(self.red_tint_alpha * 0.3)
            pygame.draw.line(
                self.danger_surface,
                (EXPLOSION_DARK_RED[0], EXPLOSION_DARK_RED[1], EXPLOSION_DARK_RED[2], alpha),
                (x, 0),
                (x, 20)
            )
            pygame.draw.line(
                self.danger_surface,
                (EXPLOSION_DARK_RED[0], EXPLOSION_DARK_RED[1], EXPLOSION_DARK_RED[2], alpha),
                (x, SCREEN_HEIGHT - 20),
                (x, SCREEN_HEIGHT)
            )
        
        for y in range(SCREEN_HEIGHT):
            alpha = int(self.red_tint_alpha * 0.3)
            pygame.draw.line(
                self.danger_surface,
                (EXPLOSION_DARK_RED[0], EXPLOSION_DARK_RED[1], EXPLOSION_DARK_RED[2], alpha),
                (0, y),
                (20, y)
            )
            pygame.draw.line(
                self.danger_surface,
                (EXPLOSION_DARK_RED[0], EXPLOSION_DARK_RED[1], EXPLOSION_DARK_RED[2], alpha),
                (SCREEN_WIDTH - 20, y),
                (SCREEN_WIDTH, y)
            )
    
    def update(self, current_lives):
        if not self.enabled:
            return
        
        was_active = self.is_active
        self.is_active = current_lives <= self.low_hp_threshold
        
        if self.is_active:
            self.flash_timer += 1
            
            if self.flash_timer >= self.flash_interval:
                self.flash_timer = 0
                self.flash_phase = 1 - self.flash_phase
            
            if not was_active:
                self.flash_timer = 0
                self.flash_phase = 1
        else:
            self.flash_phase = 0
    
    def draw(self, surface):
        if not self.enabled or not self.is_active:
            return
        
        if self.flash_phase == 1:
            surface.blit(self.danger_surface, (0, 0))


class UpgradeFlash:
    def __init__(self):
        config = POST_PROCESS_CONFIG["upgrade_flash"]
        self.enabled = config["enabled"]
        self.duration = config["duration"]
        self.gold_tint_alpha = config["gold_tint_alpha"]
        
        self.is_active = False
        self.frame = 0
        self.current_alpha = 0
        
        self.flash_surfaces = []
        self._create_flash_surfaces()
    
    def _create_flash_surfaces(self):
        self.flash_surfaces = []
        
        for intensity in [0.2, 0.4, 0.6, 0.8, 1.0]:
            surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(self.gold_tint_alpha * intensity)
            surface.fill((*ULTIMATE_GOLD, alpha))
            
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            
            for i in range(3):
                radius = int(50 + i * 50)
                gradient_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                
                gradient_alpha = int(alpha * (0.7 - i * 0.2))
                pygame.draw.circle(
                    gradient_surface,
                    (*ULTIMATE_LIGHT_GOLD, gradient_alpha),
                    (radius, radius),
                    radius
                )
                surface.blit(gradient_surface, (center_x - radius, center_y - radius))
            
            self.flash_surfaces.append(surface)
    
    def trigger(self):
        if not self.enabled:
            return
        
        self.is_active = True
        self.frame = 0
        self.current_alpha = 0
    
    def update(self):
        if not self.enabled or not self.is_active:
            return False
        
        self.frame += 1
        
        fade_in_frames = self.duration // 4
        peak_frames = self.duration // 4
        fade_out_frames = self.duration // 2
        
        if self.frame <= fade_in_frames:
            progress = self.frame / fade_in_frames
            self.current_alpha = int(self.gold_tint_alpha * progress)
        elif self.frame <= fade_in_frames + peak_frames:
            self.current_alpha = self.gold_tint_alpha
        else:
            fade_progress = (self.frame - fade_in_frames - peak_frames) / fade_out_frames
            self.current_alpha = int(self.gold_tint_alpha * (1 - fade_progress))
        
        if self.frame >= self.duration:
            self.is_active = False
            self.current_alpha = 0
            return False
        
        return True
    
    def draw(self, surface):
        if not self.enabled or not self.is_active:
            return
        
        if self.current_alpha <= 0:
            return
        
        surface_index = min(len(self.flash_surfaces) - 1, int(self.current_alpha / 20))
        
        if surface_index >= 0 and surface_index < len(self.flash_surfaces):
            temp_surface = self.flash_surfaces[surface_index].copy()
            temp_surface.set_alpha(self.current_alpha)
            surface.blit(temp_surface, (0, 0))


class PostProcessor:
    def __init__(self):
        self.motion_blur = MotionBlur()
        self.color_boost = ColorBoost()
        self.danger_flash = DangerFlash()
        self.upgrade_flash = UpgradeFlash()
        
        self.prev_surface = None
    
    def update(self, ship_position=None, ship_speed=0, combo_count=0, current_lives=3):
        if ship_position:
            self.motion_blur.update(ship_position, ship_speed)
        
        self.color_boost.update(combo_count)
        self.danger_flash.update(current_lives)
        self.upgrade_flash.update()
    
    def trigger_upgrade(self):
        self.upgrade_flash.trigger()
    
    def apply(self, surface):
        if self.prev_surface is None or self.prev_surface.get_size() != surface.get_size():
            self.prev_surface = surface.copy()
        
        result = surface
        
        result = self.color_boost.apply(result)
        
        self.danger_flash.draw(result)
        self.upgrade_flash.draw(result)
        
        self.prev_surface = result.copy()
        
        return result
    
    def draw_all_effects(self, surface):
        self.danger_flash.draw(surface)
        self.upgrade_flash.draw(surface)
