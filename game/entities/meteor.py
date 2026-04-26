import random
import pygame
from game.config import (
    SCREEN_WIDTH,
    METEOR_CONFIG,
    METEOR_SMALL, METEOR_MEDIUM, METEOR_LARGE, METEOR_SPLIT,
    darken_color_gradient
)

class Meteor:
    def __init__(self, meteor_type=None, x=None, y=None):
        if meteor_type is None:
            types = list(METEOR_CONFIG.keys())
            weights = [METEOR_CONFIG[t]["weight"] for t in types]
            meteor_type = random.choices(types, weights=weights, k=1)[0]
        
        self.type = meteor_type
        self.config = METEOR_CONFIG[meteor_type]
        
        self.max_hp = self.config["hp"]
        self.hp = self.max_hp
        
        self.width = random.randint(*self.config["width_range"])
        self.height = random.randint(*self.config["height_range"])
        
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
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.hit_effect_timer = 0
        self.hit_flash_duration = 8
        self.was_hit = False
        
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-1.5, 1.5)
    
    def get_center(self):
        return self.x + self.width // 2, self.y + self.height // 2
    
    def take_damage(self, damage=1):
        self.hp -= damage
        self.hit_effect_timer = self.hit_flash_duration
        self.was_hit = True
        return self.hp <= 0
    
    def get_current_color(self):
        if self.hit_effect_timer > 0:
            return (255, 255, 255)
        return darken_color_gradient(self.config["color"], self.hp, self.max_hp)
    
    def get_current_inner_color(self):
        if self.hit_effect_timer > 0:
            return (220, 220, 220)
        return darken_color_gradient(self.config["color_inner"], self.hp, self.max_hp)
    
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
                y=center_y + offset_y
            )
            new_meteor.speed = self.base_speed * random.uniform(0.8, 1.2)
            split_meteors.append(new_meteor)
        
        return split_meteors
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        self.rotation += self.rotation_speed
        
        if self.hit_effect_timer > 0:
            self.hit_effect_timer -= 1
        
        if self.rotation >= 360:
            self.rotation -= 360
        elif self.rotation < 0:
            self.rotation += 360
    
    def draw(self, surface):
        outer_color = self.get_current_color()
        inner_color = self.get_current_inner_color()
        
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        temp_surface = pygame.Surface((self.width + 4, self.height + 4), pygame.SRCALPHA)
        temp_rect = temp_surface.get_rect(center=(center_x, center_y))
        
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
