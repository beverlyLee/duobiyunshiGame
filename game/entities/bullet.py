import pygame
from game.config import (
    SCREEN_HEIGHT,
    YELLOW, WHITE
)

class Bullet:
    def __init__(self, x, y):
        self.width = 6
        self.height = 16
        self.x = x - self.width // 2
        self.y = y
        self.speed = 10
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = True
    
    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
        
        if self.y < -self.height:
            self.active = False
        
        return self.active
    
    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)
        pygame.draw.rect(surface, WHITE, (self.x + 1, self.y + 2, self.width - 2, self.height - 4))
