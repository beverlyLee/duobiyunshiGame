import random
import math
import pygame
from game.config import (
    BLUE, LIGHT_BLUE, DARK_BLUE,
    ORANGE, YELLOW, RED,
    DARK_RED
)

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime, fade_speed, shrink_speed):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.initial_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.fade_speed = fade_speed
        self.shrink_speed = shrink_speed
        self.alpha = 255
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        if self.lifetime > 0:
            self.alpha = int(255 * (self.lifetime / self.max_lifetime))
            self.size = self.initial_size * (self.lifetime / self.max_lifetime)
        
        return self.lifetime > 0
    
    def draw(self, surface):
        if self.alpha <= 0 or self.size <= 0:
            return
        
        temp_surface = pygame.Surface((int(self.size * 2) + 2, int(self.size * 2) + 2), pygame.SRCALPHA)
        alpha_color = (self.color[0], self.color[1], self.color[2], self.alpha)
        pygame.draw.circle(temp_surface, alpha_color, (int(self.size) + 1, int(self.size) + 1), int(self.size))
        surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def create_engine_trail(self, x, y, direction):
        for _ in range(2):
            offset_x = random.randint(-10, 10)
            vx = direction * random.uniform(1, 3) + random.uniform(-1, 1)
            vy = random.uniform(0.5, 2)
            color = random.choice([BLUE, LIGHT_BLUE, DARK_BLUE])
            size = random.uniform(3, 6)
            lifetime = random.randint(20, 40)
            particle = Particle(
                x + offset_x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=5, shrink_speed=0.1
            )
            self.particles.append(particle)
    
    def create_explosion(self, x, y, num_particles=15):
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([ORANGE, YELLOW, RED, (255, 100, 0)])
            size = random.uniform(4, 8)
            lifetime = random.randint(30, 60)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=3, shrink_speed=0.05
            )
            self.particles.append(particle)
    
    def create_collision(self, x, y, num_particles=25):
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([RED, DARK_RED, ORANGE, YELLOW])
            size = random.uniform(5, 10)
            lifetime = random.randint(40, 80)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=2, shrink_speed=0.03
            )
            self.particles.append(particle)
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)
