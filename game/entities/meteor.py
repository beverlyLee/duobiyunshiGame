import random
import math
import pygame
from game.config import (
    SCREEN_WIDTH,
    METEOR_CONFIG,
    METEOR_SMALL, METEOR_MEDIUM, METEOR_LARGE, METEOR_SPLIT,
    METEOR_TRACKER, METEOR_ARMORED, METEOR_EXPLOSIVE,
    SPECIAL_METEOR_CONFIG,
    darken_color_gradient
)

class Meteor:
    def __init__(self, meteor_type=None, x=None, y=None, ship=None, color_override=None):
        if meteor_type is None:
            types = list(METEOR_CONFIG.keys())
            weights = [METEOR_CONFIG[t]["weight"] for t in types]
            meteor_type = random.choices(types, weights=weights, k=1)[0]
        
        self.type = meteor_type
        self.config = METEOR_CONFIG[meteor_type]
        self.ship = ship
        
        if self.is_tracker() and color_override is not None:
            self.outer_color = color_override[0]
            self.inner_color = color_override[1]
        else:
            self.outer_color = self.config["color"]
            self.inner_color = self.config["color_inner"]
        
        self.max_hp = self.config["hp"]
        self.hp = self.max_hp
        
        self.armor = self.config.get("armor", 0)
        self.max_armor = self.armor
        
        self.width = random.randint(*self.config["width_range"])
        self.height = random.randint(*self.config["height_range"])
        
        if self.config.get("is_circular", False):
            min_dim = min(self.width, self.height)
            self.width = min_dim
            self.height = min_dim
        
        if x is not None:
            self.x = x - self.width // 2
        else:
            self.x = random.randint(0, max(0, SCREEN_WIDTH - self.width))
        
        if y is not None:
            self.y = y
        else:
            self.y = -self.height
        
        self.speed = random.randint(*self.config["speed_range"])
        self.base_speed = self.speed
        
        self.speed_x = 0.0
        self.target_x = self.x
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.hit_effect_timer = 0
        self.hit_flash_duration = 8
        self.was_hit = False
        
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-1.5, 1.5)
        
        self.tracking_activated = False
        self.tracking_speed = self.config.get("tracking_speed", 2.0)
        self.tracking_start_y = self.config.get("tracking_start_y", 150)
        self.tracking_direction = 0
        
        self.fuse_timer = 0
        self.fuse_time = self.config.get("fuse_time", 120)
        self.explosion_radius = self.config.get("explosion_radius", 120)
        self.explosion_damage = self.config.get("explosion_damage", 1)
        self.fuse_activated = False
        
        self.armor_hit_effect_timer = 0
        self.armor_hit_flash_duration = 12
        self.spark_particles = []
        self.spark_cooldown = 0
        
        self.glow_pulse_phase = random.random() * math.pi * 2
        self.glow_intensity = 0.5
        
        if self.is_armored():
            self.metal_shine_offset = random.random() * 360
    
    def set_ship(self, ship):
        self.ship = ship
    
    def get_center(self):
        return self.x + self.width // 2, self.y + self.height // 2
    
    def take_damage(self, damage=1):
        if self.is_armored():
            self.spark_cooldown = 6
            self._create_sparks()
        
        if self.armor > 0:
            self.armor -= damage
            if self.armor < 0:
                remaining_damage = -self.armor
                self.armor = 0
                self.hp -= remaining_damage
            self.armor_hit_effect_timer = self.armor_hit_flash_duration
            self.hit_effect_timer = self.hit_flash_duration
            self.was_hit = True
            return self.hp <= 0 and self.armor <= 0
        
        self.hp -= damage
        self.hit_effect_timer = self.hit_flash_duration
        self.was_hit = True
        return self.hp <= 0
    
    def _create_sparks(self):
        center_x, center_y = self.get_center()
        num_sparks = random.randint(3, 6)
        for _ in range(num_sparks):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            size = random.uniform(2, 4)
            lifetime = random.randint(10, 20)
            self.spark_particles.append({
                "x": center_x,
                "y": center_y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": size,
                "lifetime": lifetime,
                "max_lifetime": lifetime
            })
    
    def _update_sparks(self):
        if self.spark_cooldown > 0:
            self.spark_cooldown -= 1
        
        for spark in self.spark_particles[:]:
            spark["x"] += spark["vx"]
            spark["y"] += spark["vy"]
            spark["vy"] += 0.1
            spark["lifetime"] -= 1
            if spark["lifetime"] <= 0:
                self.spark_particles.remove(spark)
    
    def take_explosion_damage(self):
        return self.take_damage(self.explosion_damage)
    
    def is_tracker(self):
        return self.type == METEOR_TRACKER
    
    def is_armored(self):
        return self.type == METEOR_ARMORED
    
    def is_explosive(self):
        return self.type == METEOR_EXPLOSIVE
    
    def should_explode_on_destroy(self):
        return self.is_explosive()
    
    def activate_fuse(self):
        if self.is_explosive() and not self.fuse_activated:
            self.fuse_activated = True
            self.fuse_timer = 0
    
    def get_explosion_radius(self):
        return self.explosion_radius
    
    def get_current_color(self):
        if self.hit_effect_timer > 0:
            return (255, 255, 255)
        
        if self.is_armored() and self.armor > 0:
            if self.armor_hit_effect_timer > 0:
                return (255, 255, 255)
            return self.config.get("armor_color", (192, 192, 192))
        
        return darken_color_gradient(self.outer_color, self.hp, self.max_hp)
    
    def get_current_inner_color(self):
        if self.hit_effect_timer > 0:
            return (220, 220, 220)
        return darken_color_gradient(self.inner_color, self.hp, self.max_hp)
    
    def can_split(self):
        return self.type == METEOR_SPLIT and "split_count" in self.config
    
    def get_split_meteors(self):
        if not self.can_split():
            return []
        
        split_count = random.randint(*self.config["split_count"])
        split_type = self.config["split_type"]
        split_meteors = []
        
        center_x, center_y = self.get_center()
        
        for i in range(split_count):
            offset_x = random.randint(-self.width // 3, self.width // 3)
            offset_y = random.randint(-self.height // 3, self.height // 3)
            
            new_meteor = Meteor(
                meteor_type=split_type,
                x=center_x + offset_x,
                y=center_y + offset_y,
                ship=self.ship
            )
            new_meteor.speed = self.base_speed * random.uniform(0.8, 1.2)
            split_meteors.append(new_meteor)
        
        return split_meteors
    
    def update_tracking(self):
        if not self.is_tracker():
            return
        
        if not self.tracking_activated and self.y >= self.tracking_start_y:
            self.tracking_activated = True
        
        if self.tracking_activated and self.ship:
            ship_center_x = self.ship.x + self.ship.width // 2
            meteor_center_x = self.x + self.width // 2
            
            dx = ship_center_x - meteor_center_x
            
            prev_speed_x = self.speed_x
            
            if abs(dx) > 5:
                if dx > 0:
                    self.speed_x = min(self.speed_x + 0.15, self.tracking_speed)
                else:
                    self.speed_x = max(self.speed_x - 0.15, -self.tracking_speed)
            else:
                self.speed_x *= 0.95
            
            if abs(self.speed_x) > 0.1:
                if self.speed_x > 0:
                    self.tracking_direction = 1
                else:
                    self.tracking_direction = -1
            
            if abs(self.speed_x) < 0.5 and abs(prev_speed_x) >= 0.5:
                if self.speed_x > 0:
                    self.tracking_direction = 1
                elif self.speed_x < 0:
                    self.tracking_direction = -1
        
        self.x += self.speed_x
        
        if self.x < 0:
            self.x = 0
            self.speed_x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.speed_x = 0
        
        self.rect.x = self.x
    
    def update_explosive(self):
        if not self.is_explosive():
            return False
        
        if self.fuse_activated:
            self.fuse_timer += 1
            if self.fuse_timer >= self.fuse_time:
                return True
        
        return False
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        
        self.update_tracking()
        
        self.update_explosive()
        
        self._update_sparks()
        
        self.rotation += self.rotation_speed
        
        if self.hit_effect_timer > 0:
            self.hit_effect_timer -= 1
        
        if self.armor_hit_effect_timer > 0:
            self.armor_hit_effect_timer -= 1
        
        if self.rotation >= 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360
        
        self.glow_pulse_phase += 0.1
    
    def _draw_metal_texture(self, surface, rect, center_x, center_y):
        shine_pos = (self.metal_shine_offset + self.rotation) % 360
        shine_angle = math.radians(shine_pos)
        
        shine_offset_x = math.cos(shine_angle) * (self.width // 3)
        shine_offset_y = math.sin(shine_angle) * (self.height // 3)
        
        shine_surface = pygame.Surface((self.width + 4, self.height + 4), pygame.SRCALPHA)
        
        shine_x = self.width // 2 + 2 + shine_offset_x
        shine_y = self.height // 2 + 2 + shine_offset_y
        
        pygame.draw.circle(
            shine_surface,
            (255, 255, 255, 80),
            (int(shine_x), int(shine_y)),
            min(self.width, self.height) // 4
        )
        
        pygame.draw.circle(
            shine_surface,
            (200, 200, 200, 40),
            (int(shine_x - 5), int(shine_y - 5)),
            min(self.width, self.height) // 6
        )
        
        surface.blit(shine_surface, (self.x - 2, self.y - 2))
        
        for i in range(3):
            angle = math.radians(i * 120 + self.rotation)
            start_x = center_x + math.cos(angle) * (self.width // 4)
            start_y = center_y + math.sin(angle) * (self.height // 4)
            end_x = center_x + math.cos(angle + 0.3) * (self.width // 2)
            end_y = center_y + math.sin(angle + 0.3) * (self.height // 2)
            
            pygame.draw.line(
                surface,
                (100, 100, 100, 100),
                (int(start_x), int(start_y)),
                (int(end_x), int(end_y)),
                2
            )
    
    def _draw_circular_meteor(self, surface, center_x, center_y):
        outer_color = self.get_current_color()
        inner_color = self.get_current_inner_color()
        
        radius = self.width // 2
        
        pygame.draw.circle(surface, outer_color, (center_x, center_y), radius)
        
        inner_radius = radius // 2
        pygame.draw.circle(surface, inner_color, (center_x, center_y), inner_radius)
        
        if self.hp < self.max_hp:
            damage_ratio = (self.max_hp - self.hp) / self.max_hp
            crack_count = int(damage_ratio * 4)
            
            for i in range(crack_count):
                start_angle = random.uniform(0, 2 * math.pi)
                start_r = random.uniform(inner_radius * 0.5, radius * 0.8)
                end_angle = start_angle + random.uniform(-0.5, 0.5)
                end_r = random.uniform(start_r, radius * 0.9)
                
                start_x = center_x + math.cos(start_angle) * start_r
                start_y = center_y + math.sin(start_angle) * start_r
                end_x = center_x + math.cos(end_angle) * end_r
                end_y = center_y + math.sin(end_angle) * end_r
                
                pygame.draw.line(
                    surface,
                    (50, 50, 50, 180),
                    (int(start_x), int(start_y)),
                    (int(end_x), int(end_y)),
                    2
                )
    
    def _draw_glow_effect(self, surface, center_x, center_y):
        glow_color = self.config.get("glow_color", (255, 140, 0))
        
        if self.fuse_activated:
            fuse_progress = self.fuse_timer / self.fuse_time
            pulse_speed = 8 + fuse_progress * 15
            base_intensity = 0.3 + fuse_progress * 0.5
        else:
            pulse_speed = 5
            base_intensity = 0.3
        
        pulse_value = (math.sin(self.glow_pulse_phase * pulse_speed) + 1) / 2
        glow_alpha = int((base_intensity + pulse_value * 0.3) * 150)
        
        glow_radius = max(self.width, self.height) // 2 + 10
        
        glow_surface = pygame.Surface((glow_radius * 2 + 10, glow_radius * 2 + 10), pygame.SRCALPHA)
        
        for i in range(3, 0, -1):
            current_radius = glow_radius - i * 3
            alpha = glow_alpha // (i + 1)
            pygame.draw.circle(
                glow_surface,
                (*glow_color, alpha),
                (glow_radius + 5, glow_radius + 5),
                current_radius
            )
        
        surface.blit(glow_surface, (center_x - glow_radius - 5, center_y - glow_radius - 5))
    
    def _draw_tracking_arrow(self, surface, center_x, center_y):
        if not self.tracking_activated:
            return
        
        arrow_size = 12
        arrow_y = self.y - 20
        
        if self.tracking_direction == 1:
            arrow_points = [
                (center_x + arrow_size, arrow_y),
                (center_x - arrow_size, arrow_y - arrow_size // 2),
                (center_x - arrow_size, arrow_y + arrow_size // 2),
            ]
        elif self.tracking_direction == -1:
            arrow_points = [
                (center_x - arrow_size, arrow_y),
                (center_x + arrow_size, arrow_y - arrow_size // 2),
                (center_x + arrow_size, arrow_y + arrow_size // 2),
            ]
        else:
            arrow_points = [
                (center_x, arrow_y - arrow_size),
                (center_x - arrow_size // 2, arrow_y),
                (center_x + arrow_size // 2, arrow_y),
            ]
        
        arrow_color = (*self.outer_color[:3], 200)
        pygame.draw.polygon(surface, arrow_color, arrow_points)
        
        pulse_size = 6 + math.sin(self.glow_pulse_phase * 6) * 2
        pygame.draw.circle(
            surface,
            (255, 255, 255, 150),
            (center_x, self.y - 5),
            int(pulse_size),
            2
        )
    
    def _draw_spark_particles(self, surface):
        for spark in self.spark_particles:
            alpha = int(255 * (spark["lifetime"] / spark["max_lifetime"]))
            size = spark["size"] * (spark["lifetime"] / spark["max_lifetime"])
            
            spark_color = (255, 215, 0, alpha) if random.random() > 0.5 else (255, 140, 0, alpha)
            
            temp_surface = pygame.Surface((int(size * 2) + 2, int(size * 2) + 2), pygame.SRCALPHA)
            pygame.draw.circle(
                temp_surface,
                spark_color,
                (int(size) + 1, int(size) + 1),
                int(size)
            )
            surface.blit(temp_surface, (int(spark["x"] - size - 1), int(spark["y"] - size - 1)))
    
    def draw(self, surface):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        if self.is_explosive():
            self._draw_glow_effect(surface, center_x, center_y)
        
        if self.is_tracker():
            self._draw_circular_meteor(surface, center_x, center_y)
        else:
            outer_color = self.get_current_color()
            inner_color = self.get_current_inner_color()
            
            temp_surface = pygame.Surface((self.width + 4, self.height + 4), pygame.SRCALPHA)
            
            ellipse_rect = pygame.Rect(2, 2, self.width, self.height)
            pygame.draw.ellipse(temp_surface, outer_color, ellipse_rect)
            
            inner_ellipse_rect = pygame.Rect(
                2 + self.width // 6, 
                2 + self.height // 6, 
                self.width - self.width // 3, 
                self.height - self.height // 3
            )
            pygame.draw.ellipse(temp_surface, inner_color, inner_ellipse_rect)
            
            if self.hp < self.max_hp:
                damage_ratio = (self.max_hp - self.hp) / self.max_hp
                crack_count = int(damage_ratio * 4)
                
                for i in range(crack_count):
                    start_x = random.randint(int(self.width * 0.2), int(self.width * 0.8))
                    start_y = random.randint(int(self.height * 0.2), int(self.height * 0.8))
                    end_x = start_x + random.randint(-10, 10)
                    end_y = start_y + random.randint(-10, 10)
                    
                    pygame.draw.line(
                        temp_surface, 
                        (50, 50, 50, 180),
                        (start_x + 2, start_y + 2),
                        (end_x + 2, end_y + 2),
                        2
                    )
            
            rotated_surface = pygame.transform.rotate(temp_surface, self.rotation)
            new_rect = rotated_surface.get_rect(center=(center_x, center_y))
            surface.blit(rotated_surface, new_rect)
        
        if self.is_armored():
            self._draw_metal_texture(surface, None, center_x, center_y)
        
        self._draw_spark_particles(surface)
        
        if self.is_tracker():
            self._draw_tracking_arrow(surface, center_x, center_y)
        
        if self.max_hp > 1:
            hp_text = f"{self.hp}/{self.max_hp}"
            from game.core.utils import get_small_font
            font = get_small_font()
            text = font.render(hp_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(center_x, center_y))
            surface.blit(text, text_rect)
        
        if self.type == METEOR_SPLIT and self.hp > 0:
            indicator_color = (255, 100, 100, 150)
            pygame.draw.circle(
                surface, 
                indicator_color,
                (center_x, self.y - 8),
                5
            )
