import pygame
import math
from game.config import (
    SCREEN_HEIGHT,
    YELLOW, WHITE,
    BLUE_YELLOW_MIX, ICE_BLUE,
    RAINBOW_COLORS
)

class Bullet:
    def __init__(self, x, y, is_penetrating=False, is_freezing=False, penetration_count=0, size_multiplier=1.0):
        self.base_width = 6
        self.base_height = 16
        
        self.is_penetrating = is_penetrating
        self.is_freezing = is_freezing
        
        if is_penetrating:
            self.size_multiplier = size_multiplier
            self.width = int(self.base_width * size_multiplier)
            self.height = int(self.base_height * size_multiplier)
        else:
            self.size_multiplier = 1.0
            self.width = self.base_width
            self.height = self.base_height
        
        self.x = x - self.width // 2
        self.y = y
        self.speed = 10
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = True
        
        self.penetration_count = penetration_count
        self.penetrations_used = 0
    
    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
        
        if self.y < -self.height:
            self.active = False
        
        return self.active
    
    def can_penetrate(self):
        if not self.is_penetrating:
            return False
        return self.penetrations_used < self.penetration_count
    
    def use_penetration(self):
        self.penetrations_used += 1
        if self.penetrations_used >= self.penetration_count:
            self.active = False
    
    def draw(self, surface):
        if self.is_penetrating:
            outer_color = BLUE_YELLOW_MIX
            inner_color = (230, 230, 150)
        elif self.is_freezing:
            outer_color = ICE_BLUE
            inner_color = (180, 220, 255)
        else:
            outer_color = YELLOW
            inner_color = WHITE
        
        pygame.draw.rect(surface, outer_color, self.rect)
        pygame.draw.rect(surface, inner_color, (self.x + 1, self.y + 2, self.width - 2, self.height - 4))
        
        if self.is_penetrating:
            pygame.draw.circle(surface, BLUE_YELLOW_MIX, 
                             (self.x + self.width // 2, self.y + self.height // 2), 
                             self.width, 1)
            
            pygame.draw.rect(surface, (50, 150, 255), 
                           (self.x, self.y, self.width, 2))
            pygame.draw.rect(surface, (50, 150, 255), 
                           (self.x, self.y, 2, self.height))
            
            pygame.draw.rect(surface, (255, 215, 0), 
                           (self.x, self.y + self.height - 2, self.width, 2))
            pygame.draw.rect(surface, (255, 215, 0), 
                           (self.x + self.width - 2, self.y, 2, self.height))
        elif self.is_freezing:
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle)
                cx = self.x + self.width // 2
                cy = self.y + self.height // 2
                r = self.width
                x = cx + r * math.cos(rad)
                y = cy + r * math.sin(rad)
                pygame.draw.line(surface, ICE_BLUE, (cx, cy), (x, y), 1)
    
    def get_center(self):
        return self.x + self.width // 2, self.y + self.height // 2
    
    def get_trail_position(self):
        return self.x + self.width // 2, self.y + self.height
    
    def draw_with_combo_effect(self, surface, is_high_combo=False, combo_count=0):
        if not is_high_combo or combo_count < 20:
            self.draw(surface)
            return
        
        center_x, center_y = self.get_center()
        
        glow_size = int(self.width * 3)
        color_index = (pygame.time.get_ticks() // 50) % len(RAINBOW_COLORS)
        glow_color = RAINBOW_COLORS[color_index]
        
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*glow_color, 80),
            (glow_size, glow_size),
            glow_size
        )
        surface.blit(glow_surface, (int(center_x - glow_size), int(center_y - glow_size)))
        
        inner_glow_surface = pygame.Surface((self.width * 4, self.height * 2), pygame.SRCALPHA)
        next_color_index = (color_index + 1) % len(RAINBOW_COLORS)
        inner_color = RAINBOW_COLORS[next_color_index]
        
        pygame.draw.rect(
            inner_glow_surface,
            (*inner_color, 60),
            (0, 0, self.width * 4, self.height * 2)
        )
        surface.blit(inner_glow_surface, (int(self.x - self.width * 1.5), int(self.y - self.height // 2)))
        
        self.draw(surface)
