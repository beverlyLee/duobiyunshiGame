import random
import pygame
import math
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    ENVIRONMENT_CONFIG,
    EXPLOSION_YELLOW, EXPLOSION_ORANGE, EXPLOSION_RED
)

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

class ShootingStar:
    def __init__(self):
        config = ENVIRONMENT_CONFIG["meteors"]
        self.min_speed = config["min_speed"]
        self.max_speed = config["max_speed"]
        self.min_length = config["min_length"]
        self.max_length = config["max_length"]
        
        self.reset()
    
    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH - 100)
        self.y = random.randint(-100, 0)
        
        self.angle = random.uniform(math.pi / 6, math.pi / 3)
        self.speed = random.uniform(self.min_speed, self.max_speed)
        
        self.length = random.randint(self.min_length, self.max_length)
        self.lifetime = int((SCREEN_HEIGHT + self.length) / self.speed) + 50
        self.max_lifetime = self.lifetime
        
        color_choices = [EXPLOSION_YELLOW, EXPLOSION_ORANGE, (255, 255, 255)]
        self.color = random.choice(color_choices)
        
        self.active = True
        self.alpha = 255
    
    def update(self):
        if not self.active:
            return False
        
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.lifetime -= 1
        
        if self.lifetime < 30:
            self.alpha = int(255 * (self.lifetime / 30))
        
        if self.y > SCREEN_HEIGHT + self.length or self.lifetime <= 0:
            self.active = False
        
        return self.active
    
    def draw(self, surface):
        if not self.active or self.alpha <= 0:
            return
        
        end_x = self.x - self.length * math.cos(self.angle)
        end_y = self.y - self.length * math.sin(self.angle)
        
        for i in range(10):
            t = i / 10
            current_x = int(self.x * (1 - t) + end_x * t)
            current_y = int(self.y * (1 - t) + end_y * t)
            current_alpha = int(self.alpha * (1 - t * 0.7))
            current_size = int(3 * (1 - t * 0.7))
            
            if current_size > 0 and current_alpha > 0:
                temp_surface = pygame.Surface((current_size * 4, current_size * 4), pygame.SRCALPHA)
                alpha_color = (*self.color[:3], current_alpha)
                pygame.draw.circle(
                    temp_surface,
                    alpha_color,
                    (current_size * 2, current_size * 2),
                    current_size
                )
                surface.blit(temp_surface, (current_x - current_size * 2, current_y - current_size * 2))
        
        head_size = 5
        head_surface = pygame.Surface((head_size * 4, head_size * 4), pygame.SRCALPHA)
        pygame.draw.circle(
            head_surface,
            (*self.color[:3], self.alpha),
            (head_size * 2, head_size * 2),
            head_size
        )
        surface.blit(head_surface, (int(self.x) - head_size * 2, int(self.y) - head_size * 2))

class NebulaLayer:
    def __init__(self, layer_index):
        config = ENVIRONMENT_CONFIG["nebula"]
        self.color_palette = config["color_palette"]
        self.move_speed = config["move_speed"]
        self.alpha_base = config["alpha_base"]
        
        self.layer_index = layer_index
        
        self.x = random.randint(-SCREEN_WIDTH // 2, SCREEN_WIDTH // 2)
        self.y = random.randint(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2)
        
        self.radius_x = random.randint(SCREEN_WIDTH // 4, SCREEN_WIDTH)
        self.radius_y = random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT)
        
        self.vx = (random.random() - 0.5) * self.move_speed * 2
        self.vy = (random.random() - 0.5) * self.move_speed * 2
        
        color_index = random.randint(0, len(self.color_palette) - 1)
        self.base_color = self.color_palette[color_index]
        
        self.alpha_variation = random.random()
        self.pulse_speed = random.uniform(0.005, 0.015)
        self.pulse_phase = random.random() * math.pi * 2
        
        self.surface = None
        self._generate_surface()
    
    def _generate_surface(self):
        surface_width = self.radius_x * 2 + 100
        surface_height = self.radius_y * 2 + 100
        
        self.surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
        
        center_x = surface_width // 2
        center_y = surface_height // 2
        
        for i in range(200):
            angle = random.uniform(0, 2 * math.pi)
            dist_factor = random.random()
            
            dist_x = dist_factor * self.radius_x * (0.5 + random.random() * 0.5)
            dist_y = dist_factor * self.radius_y * (0.5 + random.random() * 0.5)
            
            x = center_x + dist_x * math.cos(angle)
            y = center_y + dist_y * math.sin(angle)
            
            alpha = int(self.alpha_base * (1 - dist_factor * 0.7))
            size = random.randint(2, 5)
            
            temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                temp_surface,
                (*self.base_color, alpha),
                (size, size),
                size
            )
            self.surface.blit(temp_surface, (int(x) - size, int(y) - size))
    
    def update(self, time):
        self.x += self.vx
        self.y += self.vy
        
        if self.x < -self.radius_x - 100:
            self.x = SCREEN_WIDTH + self.radius_x
        elif self.x > SCREEN_WIDTH + self.radius_x:
            self.x = -self.radius_x - 100
        
        if self.y < -self.radius_y - 100:
            self.y = SCREEN_HEIGHT + self.radius_y
        elif self.y > SCREEN_HEIGHT + self.radius_y:
            self.y = -self.radius_y - 100
        
        self.pulse_phase += self.pulse_speed
    
    def draw(self, surface):
        if not self.surface:
            return
        
        pulse = (math.sin(self.pulse_phase) + 1) / 2
        pulse_alpha = int(self.alpha_base * 0.5 + pulse * self.alpha_base * 0.5)
        
        temp_surface = self.surface.copy()
        temp_surface.set_alpha(pulse_alpha)
        
        draw_x = int(self.x - self.surface.get_width() // 2)
        draw_y = int(self.y - self.surface.get_height() // 2)
        
        surface.blit(temp_surface, (draw_x, draw_y))

class SolarFlare:
    def __init__(self):
        config = ENVIRONMENT_CONFIG["solar_flare"]
        self.duration = config["duration"]
        self.peak_intensity = config["peak_intensity"]
        self.fade_in_frames = config["fade_in_frames"]
        self.fade_out_frames = config["fade_out_frames"]
        
        self.active = False
        self.frame = 0
        self.intensity = 0
        
        self.color = (255, 200, 100)
    
    def trigger(self):
        self.active = True
        self.frame = 0
        self.intensity = 0
    
    def update(self):
        if not self.active:
            return False
        
        self.frame += 1
        
        if self.frame <= self.fade_in_frames:
            progress = self.frame / self.fade_in_frames
            self.intensity = int(self.peak_intensity * progress)
        elif self.frame <= self.duration - self.fade_out_frames:
            self.intensity = self.peak_intensity
        else:
            fade_progress = (self.frame - (self.duration - self.fade_out_frames)) / self.fade_out_frames
            self.intensity = int(self.peak_intensity * (1 - fade_progress))
        
        if self.frame >= self.duration:
            self.active = False
            self.intensity = 0
        
        return self.active
    
    def draw(self, surface):
        if not self.active or self.intensity <= 0:
            return
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = min(255, self.intensity)
        overlay.fill((*self.color, alpha))
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 4
        
        for i in range(5, 0, -1):
            radius = int(150 + i * 50)
            alpha_gradient = int(alpha * (0.8 - i * 0.12))
            
            gradient_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                gradient_surface,
                (255, 255, 200, alpha_gradient),
                (radius, radius),
                radius
            )
            overlay.blit(gradient_surface, (center_x - radius, center_y - radius))
        
        surface.blit(overlay, (0, 0))

class StarField:
    def __init__(self):
        self.stars = []
        self.num_stars = 150
        self.time = 0
        
        for _ in range(self.num_stars):
            self.stars.append(Star())
        
        self.gradient_surface = self.create_gradient()
        
        self.config = ENVIRONMENT_CONFIG
        
        self.shooting_stars = []
        self.max_shooting_stars = 3
        
        self.nebula_layers = []
        if self.config["nebula"]["enabled"]:
            num_layers = self.config["nebula"]["layer_count"]
            for i in range(num_layers):
                self.nebula_layers.append(NebulaLayer(i))
        
        self.solar_flare = None
        if self.config["solar_flare"]["enabled"]:
            self.solar_flare = SolarFlare()
        
        self.meteor_spawn_chance = self.config["meteors"]["spawn_chance"]
        self.solar_flare_chance = self.config["solar_flare"]["spawn_chance"]
    
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
        
        if self.config["meteors"]["enabled"]:
            if len(self.shooting_stars) < self.max_shooting_stars:
                if random.random() < self.meteor_spawn_chance:
                    self.shooting_stars.append(ShootingStar())
            
            for meteor in self.shooting_stars[:]:
                if not meteor.update():
                    self.shooting_stars.remove(meteor)
        
        for nebula in self.nebula_layers:
            nebula.update(self.time)
        
        if self.solar_flare:
            if not self.solar_flare.active and random.random() < self.solar_flare_chance:
                self.solar_flare.trigger()
            self.solar_flare.update()
    
    def draw(self, surface):
        surface.blit(self.gradient_surface, (0, 0))
        
        for nebula in self.nebula_layers:
            nebula.draw(surface)
        
        for star in self.stars:
            star.draw(surface, self.time)
        
        for meteor in self.shooting_stars:
            meteor.draw(surface)
        
        if self.solar_flare:
            self.solar_flare.draw(surface)
