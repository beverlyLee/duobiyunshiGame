import random
import pygame
from game.config import SCREEN_WIDTH

class Meteor:
    def __init__(self):
        self.width = random.randint(30, 60)
        self.height = random.randint(30, 60)
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = random.randint(3, 8)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_center(self):
        return self.x + self.width // 2, self.y + self.height // 2
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
    
    def draw(self, surface):
        pygame.draw.ellipse(surface, (139, 69, 19), (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(surface, (160, 82, 45), (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
