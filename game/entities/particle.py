import random
import math
import pygame
from game.config import (
    BLUE, LIGHT_BLUE, DARK_BLUE,
    ORANGE, YELLOW, RED,
    DARK_RED, WHITE,
    ENERGY_SHIELD_PURPLE, ENERGY_SHIELD_LIGHT_PURPLE,
    ULTIMATE_GOLD, ULTIMATE_LIGHT_GOLD,
    EXPLOSION_ORANGE, EXPLOSION_LIGHT_ORANGE,
    EXPLOSION_YELLOW, EXPLOSION_GOLD,
    EXPLOSION_RED, EXPLOSION_DARK_RED, EXPLOSION_BRIGHT_RED,
    BULLET_TRAIL_YELLOW, BULLET_TRAIL_ORANGE,
    RAINBOW_COLORS,
    METEOR_PARTICLE_CONFIG,
    METEOR_SMALL, METEOR_MEDIUM, METEOR_LARGE
)

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime, fade_speed, shrink_speed, 
                 rotation_speed=0, acceleration=0, gravity=0, color_gradient=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.initial_color = color
        self.size = size
        self.initial_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.fade_speed = fade_speed
        self.shrink_speed = shrink_speed
        self.alpha = 255
        
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = rotation_speed
        
        self.acceleration = acceleration
        self.gravity = gravity
        
        self.color_gradient = color_gradient
        self.color_phase = 0
        self.color_phase_speed = 0.1
    
    def update(self):
        if self.acceleration != 0:
            speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
            if speed > 0:
                speed += self.acceleration
                angle = math.atan2(self.vy, self.vx)
                self.vx = speed * math.cos(angle)
                self.vy = speed * math.sin(angle)
        
        if self.gravity != 0:
            self.vy += self.gravity
        
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        if self.rotation_speed != 0:
            self.rotation += self.rotation_speed
            if self.rotation >= 360:
                self.rotation -= 360
            elif self.rotation < 0:
                self.rotation += 360
        
        if self.color_gradient:
            self.color_phase += self.color_phase_speed
            color_index = int(self.color_phase) % len(self.color_gradient)
            t = (self.color_phase - int(self.color_phase))
            color1 = self.color_gradient[color_index]
            color2 = self.color_gradient[(color_index + 1) % len(self.color_gradient)]
            self.color = (
                int(color1[0] * (1 - t) + color2[0] * t),
                int(color1[1] * (1 - t) + color2[1] * t),
                int(color1[2] * (1 - t) + color2[2] * t)
            )
        
        if self.lifetime > 0:
            self.alpha = int(255 * (self.lifetime / self.max_lifetime))
            self.size = self.initial_size * (self.lifetime / self.max_lifetime)
        
        return self.lifetime > 0
    
    def draw(self, surface):
        if self.alpha <= 0 or self.size <= 0:
            return
        
        temp_surface = pygame.Surface((int(self.size * 2) + 2, int(self.size * 2) + 2), pygame.SRCALPHA)
        alpha_color = (self.color[0], self.color[1], self.color[2], self.alpha)
        
        if self.rotation_speed != 0:
            rotated_surface = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
            center = int(self.size * 2)
            points = self._get_rotated_shape_points(center, center, int(self.size))
            pygame.draw.polygon(rotated_surface, alpha_color, points)
            surface.blit(rotated_surface, (int(self.x - center), int(self.y - center)))
        else:
            pygame.draw.circle(temp_surface, alpha_color, (int(self.size) + 1, int(self.size) + 1), int(self.size))
            surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))
    
    def _get_rotated_shape_points(self, cx, cy, radius):
        num_points = 5
        angle_step = 360 / num_points
        points = []
        for i in range(num_points):
            angle = math.radians(self.rotation + i * angle_step)
            if i % 2 == 0:
                r = radius
            else:
                r = radius * 0.5
            points.append((
                cx + r * math.cos(angle),
                cy + r * math.sin(angle)
            ))
        return points

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
    
    def create_layered_explosion(self, x, y, meteor_type=METEOR_MEDIUM, meteor_size=None):
        config = METEOR_PARTICLE_CONFIG.get(meteor_type, METEOR_PARTICLE_CONFIG[METEOR_MEDIUM])
        base_count = config["base_count"]
        size_multiplier = config["size_multiplier"]
        
        if meteor_size:
            if meteor_size < 30:
                base_count = 10
                size_multiplier = 0.8
            elif meteor_size < 55:
                base_count = 20
                size_multiplier = 1.0
            else:
                base_count = 30
                size_multiplier = 1.3
        
        outer_count = int(base_count * 0.5)
        middle_count = int(base_count * 0.35)
        inner_count = int(base_count * 0.15)
        
        for _ in range(outer_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 10)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([EXPLOSION_ORANGE, EXPLOSION_LIGHT_ORANGE, (255, 120, 0)])
            size = random.uniform(4, 10) * size_multiplier
            lifetime = random.randint(25, 45)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=4, shrink_speed=0.05,
                acceleration=-0.1
            )
            self.particles.append(particle)
        
        for _ in range(middle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 7)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([EXPLOSION_YELLOW, EXPLOSION_GOLD, (255, 230, 100)])
            size = random.uniform(3, 7) * size_multiplier
            lifetime = random.randint(35, 55)
            rotation_speed = random.choice([-8, -4, 4, 8])
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=3, shrink_speed=0.04,
                rotation_speed=rotation_speed,
                acceleration=-0.05
            )
            self.particles.append(particle)
        
        for _ in range(inner_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle) - random.uniform(1, 3)
            color = random.choice([EXPLOSION_RED, EXPLOSION_DARK_RED, EXPLOSION_BRIGHT_RED])
            size = random.uniform(2, 5) * size_multiplier
            lifetime = random.randint(45, 75)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=2, shrink_speed=0.02,
                gravity=-0.05
            )
            self.particles.append(particle)
        
        self.shockwaves.append(Shockwave(x, y, 30 * size_multiplier, EXPLOSION_LIGHT_ORANGE, 25))
        self.shockwaves.append(Shockwave(x, y, 20 * size_multiplier, EXPLOSION_YELLOW, 20))
    
    def create_bullet_trail(self, x, y, is_high_combo=False, is_penetrating=False):
        if is_high_combo:
            self._create_rainbow_trail(x, y)
        else:
            self._create_yellow_trail(x, y)
        
        if is_penetrating:
            self._create_penetration_shockwave(x, y)
    
    def _create_yellow_trail(self, x, y):
        for _ in range(3):
            offset_x = random.randint(-2, 2)
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(1, 3)
            color = random.choice([BULLET_TRAIL_YELLOW, BULLET_TRAIL_ORANGE, (255, 220, 100)])
            size = random.uniform(1.5, 3.5)
            lifetime = random.randint(8, 15)
            particle = Particle(
                x + offset_x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=15, shrink_speed=0.1
            )
            self.particles.append(particle)
    
    def _create_rainbow_trail(self, x, y):
        for _ in range(5):
            offset_x = random.randint(-4, 4)
            vx = random.uniform(-1, 1)
            vy = random.uniform(1, 4)
            color_index = random.randint(0, len(RAINBOW_COLORS) - 1)
            color = RAINBOW_COLORS[color_index]
            next_color_index = (color_index + 1) % len(RAINBOW_COLORS)
            color_gradient = [color, RAINBOW_COLORS[next_color_index]]
            size = random.uniform(2, 5)
            lifetime = random.randint(10, 20)
            particle = Particle(
                x + offset_x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=12, shrink_speed=0.08,
                color_gradient=color_gradient
            )
            self.particles.append(particle)
        
        self._create_rainbow_glow(x, y)
    
    def _create_rainbow_glow(self, x, y):
        for _ in range(2):
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            vx = random.uniform(-0.3, 0.3)
            vy = random.uniform(0.5, 1.5)
            color_index = random.randint(0, len(RAINBOW_COLORS) - 1)
            color = RAINBOW_COLORS[color_index]
            next_color_index = (color_index + 1) % len(RAINBOW_COLORS)
            color_gradient = [color, RAINBOW_COLORS[next_color_index], RAINBOW_COLORS[color_index]]
            size = random.uniform(3, 7)
            lifetime = random.randint(12, 25)
            particle = Particle(
                x + offset_x, y + offset_y,
                vx, vy,
                color, size, lifetime,
                fade_speed=10, shrink_speed=0.06,
                color_gradient=color_gradient
            )
            self.particles.append(particle)
    
    def _create_penetration_shockwave(self, x, y):
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([(100, 180, 255), (150, 220, 255), (200, 240, 255)])
            size = random.uniform(2, 4)
            lifetime = random.randint(10, 20)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=15, shrink_speed=0.1
            )
            self.particles.append(particle)
    
    def create_upgrade_flash_particles(self, x, y):
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([ULTIMATE_GOLD, ULTIMATE_LIGHT_GOLD, (255, 230, 150), (255, 255, 200)])
            size = random.uniform(3, 10)
            lifetime = random.randint(20, 40)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=5, shrink_speed=0.05,
                acceleration=-0.1
            )
            self.particles.append(particle)
        
        self.shockwaves.append(Shockwave(x, y, 100, ULTIMATE_GOLD, 30))
        self.shockwaves.append(Shockwave(x, y, 80, ULTIMATE_LIGHT_GOLD, 25))
    
    def create_danger_particles(self, x, y):
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([EXPLOSION_RED, EXPLOSION_DARK_RED, (200, 50, 50)])
            size = random.uniform(2, 5)
            lifetime = random.randint(15, 30)
            particle = Particle(
                x, y,
                vx, vy,
                color, size, lifetime,
                fade_speed=8, shrink_speed=0.08
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
