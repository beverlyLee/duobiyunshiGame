import random
import pygame
import math
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class Star:
    def __init__(self):
        self.reset(True)
    
    def reset(self, random_y=False):
        self.x = random.randint(0, SCREEN_WIDTH - 1)
        if random_y:
            self.y = random.randint(0, SCREEN_HEIGHT - 1)
        else:
            self.y = -5
        
        self.size = random.uniform(0.5, 3.0)
        self.speed = self.size * 0.5 + 0.2
        self.brightness = random.randint(100, 255)
        self.twinkle_speed = random.uniform(0.02, 0.08)
        self.twinkle_offset = random.uniform(0, math.pi * 2)
        self.layer = random.choice([0, 1, 2])
        
        if self.layer == 0:
            self.speed *= 0.3
            self.brightness = random.randint(50, 120)
            self.size *= 0.6
        elif self.layer == 1:
            self.speed *= 0.6
            self.brightness = random.randint(100, 180)
            self.size *= 0.8
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.reset(False)
    
    def get_color(self, time):
        twinkle = math.sin(time * self.twinkle_speed + self.twinkle_offset)
        twinkle_factor = 0.7 + twinkle * 0.3
        current_brightness = int(self.brightness * twinkle_factor)
        current_brightness = max(20, min(255, current_brightness))
        
        if self.layer == 0:
            return (current_brightness, current_brightness, current_brightness)
        elif self.layer == 1:
            blue_tint = min(50, int(current_brightness * 0.2))
            return (current_brightness, current_brightness, min(255, current_brightness + blue_tint))
        else:
            return (current_brightness, current_brightness, current_brightness)
    
    def draw(self, surface, time):
        color = self.get_color(time)
        
        if self.size > 1.5:
            glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (*color, 30),
                (int(self.x), int(self.y)),
                int(self.size * 2)
            )
            surface.blit(glow_surface, (0, 0))
        
        pygame.draw.circle(
            surface,
            color,
            (int(self.x), int(self.y)),
            int(self.size)
        )

class StarField:
    def __init__(self):
        self.stars = []
        self.num_stars = 150
        self.time = 0
        
        for _ in range(self.num_stars):
            self.stars.append(Star())
        
        self.gradient_surface = self.create_gradient()
    
    def create_gradient(self):
        gradient = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            
            top_color = (5, 5, 20)
            middle_color = (10, 10, 35)
            bottom_color = (15, 10, 25)
            
            if progress < 0.5:
                mix = progress * 2
                r = int(top_color[0] * (1 - mix) + middle_color[0] * mix)
                g = int(top_color[1] * (1 - mix) + middle_color[1] * mix)
                b = int(top_color[2] * (1 - mix) + middle_color[2] * mix)
            else:
                mix = (progress - 0.5) * 2
                r = int(middle_color[0] * (1 - mix) + bottom_color[0] * mix)
                g = int(middle_color[1] * (1 - mix) + bottom_color[1] * mix)
                b = int(middle_color[2] * (1 - mix) + bottom_color[2] * mix)
            
            pygame.draw.line(gradient, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        return gradient
    
    def update(self):
        self.time += 1
        for star in self.stars:
            star.update()
    
    def draw(self, surface):
        surface.blit(self.gradient_surface, (0, 0))
        
        for star in self.stars:
            star.draw(surface, self.time)
