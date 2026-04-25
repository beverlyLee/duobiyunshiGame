import pygame
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BLUE, RED
)

class Ship:
    def __init__(self):
        self.width = 60
        self.height = 40
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 80
        self.speed = 7
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.direction = 0
        self.is_moving = False
        self.prev_x = self.x
    
    def update(self, keys):
        self.prev_x = self.x
        self.is_moving = False
        self.direction = 0
        
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
            self.is_moving = True
            self.direction = -1
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            self.is_moving = True
            self.direction = 1
        
        self.rect.x = self.x
        self.rect.y = self.y
    
    def get_engine_position(self):
        return self.x + self.width // 2, self.y + self.height
    
    def draw(self, surface):
        pygame.draw.polygon(surface, BLUE, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        pygame.draw.rect(surface, RED, (self.x + 15, self.y + 25, 30, 15))
