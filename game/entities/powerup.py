import random
import math
import pygame
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE,
    POWERUP_CONFIG
)
from game.core.utils import get_small_font

class PowerUp:
    def __init__(self, powerup_type=None):
        if powerup_type is None:
            types = list(POWERUP_CONFIG.keys())
            weights = [30, 25, 25, 20]
            powerup_type = random.choices(types, weights=weights, k=1)[0]
        
        self.type = powerup_type
        self.config = POWERUP_CONFIG[powerup_type]
        self.width = 40
        self.height = 40
        self.x = random.randint(20, SCREEN_WIDTH - self.width - 20)
        self.y = -self.height
        self.speed = 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.pulse_timer = 0
        self.rotation = 0
    
    def get_center(self):
        return self.x + self.width // 2, self.y + self.height // 2
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        self.pulse_timer += 0.1
        self.rotation += 2
        return self.y < SCREEN_HEIGHT + self.height
    
    def draw(self, surface):
        pulse_size = int(5 * math.sin(self.pulse_timer))
        
        pygame.draw.ellipse(
            surface, self.config["color"],
            (self.x - pulse_size, self.y - pulse_size,
             self.width + pulse_size * 2, self.height + pulse_size * 2),
            3
        )
        
        inner_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        inner_color = (*self.config["color"], 180)
        pygame.draw.ellipse(inner_surface, inner_color, (0, 0, self.width, self.height))
        
        rotated_surface = pygame.transform.rotate(inner_surface, self.rotation)
        new_rect = rotated_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(rotated_surface, new_rect)
        
        symbol_text = get_small_font().render(self.config["symbol"], True, WHITE)
        symbol_rect = symbol_text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(symbol_text, symbol_rect)
