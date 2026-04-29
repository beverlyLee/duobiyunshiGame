import random
import math
import pygame
from game.config import (
    BLUE, LIGHT_BLUE, DARK_BLUE,
    ORANGE, YELLOW, RED,
    DARK_RED, WHITE,
    ENERGY_SHIELD_PURPLE, ENERGY_SHIELD_LIGHT_PURPLE,
    ULTIMATE_GOLD, ULTIMATE_LIGHT_GOLD
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

class Shockwave:
    def __init__(self, x, y, max_radius, color, duration):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.color = color
        self.duration = duration
        self.lifetime = duration
        self.max_lifetime = duration
        self.radius = 5
        self.alpha = 255
    
    def update(self):
        self.lifetime -= 1
        
        progress = 1 - (self.lifetime / self.max_lifetime)
        self.radius = 5 + (self.max_radius - 5) * progress
        self.alpha = int(200 * (1 - progress))
        
        return self.lifetime > 0
    
    def draw(self, surface):
        if self.alpha <= 0:
            return
        
        temp_surface = pygame.Surface((int(self.radius * 2) + 4, int(self.radius * 2) + 4), pygame.SRCALPHA)
        alpha_color = (self.color[0], self.color[1], self.color[2], self.alpha)
        pygame.draw.circle(
            temp_surface,
            alpha_color,
            (int(self.radius) + 2, int(self.radius) + 2),
            int(self.radius),
            max(1, int(6 * (1 - self.lifetime / self.max_lifetime)) + 1)
        )
        surface.blit(temp_surface, (int(self.x - self.radius - 2), int(self.y - self.radius - 2)))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.shockwaves = []
    
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
    
    def create_large_explosion(self, x, y, radius=120):
        core_colors = [(255, 100, 0), ORANGE, YELLOW, RED, (255, 50, 0)]
        
        for _ in range(60):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice(core_colors)
            size = random.uniform(5, 15)
            lifetime = random.randint(40, 100)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=2, shrink_speed=0.02
            )
            self.particles.append(particle)
        
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, radius * 0.6)
            px = x + math.cos(angle) * dist
            py = y + math.sin(angle) * dist
            speed = random.uniform(1, 4)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([(255, 150, 50), (255, 200, 100), (255, 220, 150)])
            size = random.uniform(3, 8)
            lifetime = random.randint(20, 50)
            particle = Particle(
                px, py,
                vx, vy,
                color, size, lifetime,
                fade_speed=3, shrink_speed=0.04
            )
            self.particles.append(particle)
        
        self.shockwaves.append(Shockwave(x, y, radius, (255, 150, 50), 40))
        self.shockwaves.append(Shockwave(x, y, radius * 0.8, (255, 200, 100), 30))
        self.shockwaves.append(Shockwave(x, y, radius * 0.6, WHITE, 20))
    
    def create_spark(self, x, y, direction):
        for _ in range(3):
            base_angle = math.atan2(direction[1], direction[0])
            angle = base_angle + random.uniform(-0.3, 0.3)
            speed = random.uniform(4, 8)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([YELLOW, ORANGE, WHITE])
            size = random.uniform(2, 4)
            lifetime = random.randint(15, 30)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=5, shrink_speed=0.08
            )
            self.particles.append(particle)
    
    def create_knockback_shockwave(self, x, y, radius=40):
        self.shockwaves.append(Shockwave(x, y, radius, ENERGY_SHIELD_PURPLE, 30))
        self.shockwaves.append(Shockwave(x, y, int(radius * 0.7), ENERGY_SHIELD_LIGHT_PURPLE, 20))
        
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([ENERGY_SHIELD_PURPLE, ENERGY_SHIELD_LIGHT_PURPLE])
            size = random.uniform(3, 7)
            lifetime = random.randint(20, 40)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=3, shrink_speed=0.04
            )
            self.particles.append(particle)
    
    def create_energy_wave_particles(self, x, y, radius, phase):
        wave_color = ENERGY_SHIELD_PURPLE if phase % 2 == 0 else ENERGY_SHIELD_LIGHT_PURPLE
        
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            offset_radius = radius + random.uniform(-5, 5)
            px = x + math.cos(angle) * offset_radius
            py = y + math.sin(angle) * offset_radius
            
            vx = math.cos(angle) * random.uniform(0.5, 1.5)
            vy = math.sin(angle) * random.uniform(0.5, 1.5)
            
            size = random.uniform(2, 4)
            lifetime = random.randint(15, 25)
            particle = Particle(
                px, py,
                vx, vy,
                wave_color, size, lifetime,
                fade_speed=4, shrink_speed=0.06
            )
            self.particles.append(particle)
    
    def create_ship_glow_particles(self, x, y, phase):
        glow_color = ULTIMATE_GOLD if phase % 2 == 0 else ULTIMATE_LIGHT_GOLD
        
        for _ in range(2):
            angle = random.uniform(0, 2 * math.pi)
            offset_radius = random.uniform(20, 35)
            px = x + math.cos(angle) * offset_radius
            py = y + math.sin(angle) * offset_radius
            
            vx = math.cos(angle) * random.uniform(0.3, 0.8)
            vy = math.sin(angle) * random.uniform(0.3, 0.8) + random.uniform(-0.2, 0.2)
            
            size = random.uniform(3, 6)
            lifetime = random.randint(20, 35)
            particle = Particle(
                px, py,
                vx, vy,
                glow_color, size, lifetime,
                fade_speed=3, shrink_speed=0.05
            )
            self.particles.append(particle)
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
        self.shockwaves = [s for s in self.shockwaves if s.update()]
    
    def draw(self, surface):
        for shockwave in self.shockwaves:
            shockwave.draw(surface)
        
        for particle in self.particles:
            particle.draw(surface)
