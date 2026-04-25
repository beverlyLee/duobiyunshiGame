import pygame
import random
import sys
import os
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (100, 200, 255)
DARK_BLUE = (50, 100, 200)
DARK_RED = (200, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("躲避陨石")
clock = pygame.time.Clock()

def get_chinese_font(size):
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/SimHei.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
    
    try:
        return pygame.font.SysFont("pingfang", size)
    except:
        try:
            return pygame.font.SysFont("stheitisc", size)
        except:
            return pygame.font.Font(None, size)

font = get_chinese_font(36)
large_font = get_chinese_font(64)
medium_font = get_chinese_font(48)
small_font = get_chinese_font(28)

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

class FloatingText:
    def __init__(self, x, y, text, color=YELLOW, duration=60, float_speed=1.5, font_size=28):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.max_duration = duration
        self.float_speed = float_speed
        self.alpha = 255
        self.font = get_chinese_font(font_size)
    
    def update(self):
        self.y -= self.float_speed
        self.duration -= 1
        
        if self.duration > 0:
            fade_start = self.max_duration // 2
            if self.duration < fade_start:
                self.alpha = int(255 * (self.duration / fade_start))
        
        return self.duration > 0
    
    def draw(self, surface):
        if self.alpha <= 0 or self.duration <= 0:
            return
        
        text_surf = self.font.render(self.text, True, self.color)
        
        if self.alpha < 255:
            temp_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
            temp_surf.fill((255, 255, 255, self.alpha))
            text_surf.blit(temp_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        text_rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, text_rect)

class FloatingTextManager:
    def __init__(self):
        self.floating_texts = []
    
    def add_text(self, x, y, text, color=YELLOW, duration=60, float_speed=1.5, font_size=28):
        self.floating_texts.append(FloatingText(x, y, text, color, duration, float_speed, font_size))
    
    def add_score_text(self, x, y, score_amount):
        self.add_text(x, y, f"+{score_amount}", GREEN, duration=90, float_speed=1.2, font_size=32)
    
    def add_center_message(self, text, color=YELLOW, duration=120):
        self.add_text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, text, color, duration, float_speed=0, font_size=48)
    
    def update(self):
        self.floating_texts = [t for t in self.floating_texts if t.update()]
    
    def draw(self, surface):
        for text in self.floating_texts:
            text.draw(surface)

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

POWERUP_SHIELD = "shield"
POWERUP_SPEED = "speed"
POWERUP_SLOW = "slow"
POWERUP_SCORE = "score"

POWERUP_CONFIG = {
    POWERUP_SHIELD: {
        "color": (100, 200, 255),
        "symbol": "盾",
        "name": "护盾激活！",
        "duration": FPS * 8,
    },
    POWERUP_SPEED: {
        "color": (255, 255, 0),
        "symbol": "快",
        "name": "加速！",
        "duration": FPS * 5,
    },
    POWERUP_SLOW: {
        "color": (150, 100, 255),
        "symbol": "慢",
        "name": "陨石减速！",
        "duration": FPS * 5,
    },
    POWERUP_SCORE: {
        "color": (255, 200, 0),
        "symbol": "分",
        "name": "+50分！",
        "duration": 0,
    }
}

class PowerUp:
    def __init__(self, powerup_type=None):
        if powerup_type is None:
            types = list(POWERUP_CONFIG.keys())
            weights = [30, 25, 25, 20]
            powerup_type = random.choices(types, weights=weights, k=1)[0]
        
        self.type = powerup_type
        self.config = POWERUP_CONFIG[powerup_type]
        self.width = 40
        self.height = 40
        self.x = random.randint(20, SCREEN_WIDTH - self.width - 20)
        self.y = -self.height
        self.speed = 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.pulse_timer = 0
        self.rotation = 0
    
    def get_center(self):
        return self.x + self.width // 2, self.y + self.height // 2
    
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
        self.pulse_timer += 0.1
        self.rotation += 2
        return self.y < SCREEN_HEIGHT + self.height
    
    def draw(self, surface):
        pulse_size = int(5 * math.sin(self.pulse_timer))
        
        pygame.draw.ellipse(
            surface, self.config["color"],
            (self.x - pulse_size, self.y - pulse_size,
             self.width + pulse_size * 2, self.height + pulse_size * 2),
            3
        )
        
        inner_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        inner_color = (*self.config["color"], 180)
        pygame.draw.ellipse(inner_surface, inner_color, (0, 0, self.width, self.height))
        
        rotated_surface = pygame.transform.rotate(inner_surface, self.rotation)
        new_rect = rotated_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(rotated_surface, new_rect)
        
        symbol_text = small_font.render(self.config["symbol"], True, WHITE)
        symbol_rect = symbol_text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(symbol_text, symbol_rect)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.original_x = x
        self.original_y = y
        self.original_width = width
        self.original_height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.scale_factor = 1.0
        self.target_scale = 1.0
        self.hover_scale = 1.08
    
    def update_scale(self, is_hovered):
        if is_hovered:
            self.target_scale = self.hover_scale
        else:
            self.target_scale = 1.0
        
        scale_diff = self.target_scale - self.scale_factor
        self.scale_factor += scale_diff * 0.2
        
        if abs(self.scale_factor - self.target_scale) < 0.001:
            self.scale_factor = self.target_scale
        
        new_width = int(self.original_width * self.scale_factor)
        new_height = int(self.original_height * self.scale_factor)
        new_x = self.original_x - (new_width - self.original_width) // 2
        new_y = self.original_y - (new_height - self.original_height) // 2
        self.rect = pygame.Rect(new_x, new_y, new_width, new_height)
    
    def draw(self, surface, mouse_pos):
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        if is_hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
        
        self.update_scale(is_hovered)
        
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surf = small_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.rect.collidepoint(mouse_pos) and mouse_clicked

class Game:
    def __init__(self):
        self.ship = Ship()
        self.meteors = []
        self.powerups = []
        self.particle_system = ParticleSystem()
        self.text_manager = FloatingTextManager()
        self.score = 0
        self.lives = 3
        self.max_lives = 3
        self.game_over = False
        self.paused = False
        self.meteor_timer = 0
        self.meteor_interval = 60
        self.game_started = False
        self.collision_happened = False
        
        self.collision_delay = 0
        self.collision_delay_frames = FPS * 2
        self.flash_timer = 0
        self.flash_interval = 5
        self.show_flash = False
        self.collision_particle_timer = 0
        self.collision_x = 0
        self.collision_y = 0
        
        self.warning_flash = False
        self.warning_flash_timer = 0
        self.warning_flash_duration = FPS * 1
        self.warning_flash_interval = 8
        
        self.powerup_timer = 0
        self.powerup_interval = FPS * 3
        
        self.has_shield = False
        self.shield_duration = 0
        self.shield_color = POWERUP_CONFIG[POWERUP_SHIELD]["color"]
        
        self.speed_boost = False
        self.speed_boost_duration = 0
        self.base_speed = 7
        
        self.meteor_slow = False
        self.meteor_slow_duration = 0
        self.base_meteor_speed_range = (3, 8)
        
        self.start_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20,
            200, 50, "开始游戏", GREEN, (0, 200, 0)
        )
        
        self.pause_continue_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 10,
            200, 50, "继续游戏", GREEN, (0, 200, 0)
        )
        self.pause_quit_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80,
            200, 50, "退出游戏", RED, (200, 0, 0)
        )
        
        self.game_over_restart_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50,
            200, 50, "重新开始", GREEN, (0, 200, 0)
        )
        self.game_over_quit_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120,
            200, 50, "退出游戏", RED, (200, 0, 0)
        )
    
    def reset(self):
        self.ship = Ship()
        self.meteors = []
        self.powerups = []
        self.particle_system = ParticleSystem()
        self.text_manager = FloatingTextManager()
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paused = False
        self.meteor_timer = 0
        self.meteor_interval = 60
        self.game_started = True
        self.collision_happened = False
        
        self.collision_delay = 0
        self.flash_timer = 0
        self.show_flash = False
        self.collision_particle_timer = 0
        
        self.warning_flash = False
        self.warning_flash_timer = 0
        
        self.powerup_timer = 0
        
        self.has_shield = False
        self.shield_duration = 0
        
        self.speed_boost = False
        self.speed_boost_duration = 0
        
        self.meteor_slow = False
        self.meteor_slow_duration = 0
    
    def spawn_meteor(self):
        self.meteor_timer += 1
        if self.meteor_timer >= self.meteor_interval:
            self.meteors.append(Meteor())
            self.meteor_timer = 0
            if self.meteor_interval > 20:
                self.meteor_interval -= 0.5
    
    def spawn_powerup(self):
        self.powerup_timer += 1
        if self.powerup_timer >= self.powerup_interval:
            self.powerups.append(PowerUp())
            self.powerup_timer = 0
            self.powerup_interval = FPS * random.randint(3, 6)
    
    def check_collisions(self):
        for meteor in self.meteors[:]:
            if self.ship.rect.colliderect(meteor.rect):
                ship_center = (self.ship.x + self.ship.width // 2, 
                               self.ship.y + self.ship.height // 2)
                meteor_center = meteor.get_center()
                
                if self.has_shield:
                    self.has_shield = False
                    self.shield_duration = 0
                    self.particle_system.create_collision(meteor_center[0], meteor_center[1], 25)
                    self.meteors.remove(meteor)
                    self.text_manager.add_text(
                        SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                        "护盾抵消！",
                        self.shield_color, duration=90, float_speed=0, font_size=40
                    )
                    self.particle_system.create_engine_trail(ship_center[0], ship_center[1], 0)
                    continue
                
                if not self.collision_happened:
                    self.particle_system.create_collision(ship_center[0], ship_center[1], 50)
                    self.particle_system.create_collision(meteor_center[0], meteor_center[1], 35)
                    
                    self.collision_x = (ship_center[0] + meteor_center[0]) // 2
                    self.collision_y = (ship_center[1] + meteor_center[1]) // 2
                    
                    self.lives -= 1
                    
                    if self.lives <= 0:
                        self.collision_happened = True
                        self.collision_delay = self.collision_delay_frames
                        self.flash_timer = 0
                        self.collision_particle_timer = 0
                    else:
                        self.meteors.remove(meteor)
                        self.warning_flash = True
                        self.warning_flash_timer = 0
                        self.text_manager.add_text(
                            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                            f"生命值 -1！剩余 {self.lives} 条命",
                            RED, duration=90, float_speed=0, font_size=36
                        )
                return True
        return False
    
    def check_powerup_collisions(self):
        for powerup in self.powerups[:]:
            if self.ship.rect.colliderect(powerup.rect):
                powerup_center = powerup.get_center()
                
                for _ in range(15):
                    self.particle_system.create_collision(
                        powerup_center[0], powerup_center[1], 3
                    )
                
                if powerup.type == POWERUP_SHIELD:
                    self.has_shield = True
                    self.shield_duration = powerup.config["duration"]
                elif powerup.type == POWERUP_SPEED:
                    self.speed_boost = True
                    self.speed_boost_duration = powerup.config["duration"]
                elif powerup.type == POWERUP_SLOW:
                    self.meteor_slow = True
                    self.meteor_slow_duration = powerup.config["duration"]
                elif powerup.type == POWERUP_SCORE:
                    self.score += 50
                    self.text_manager.add_score_text(80, 30, 50)
                
                self.text_manager.add_text(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                    powerup.config["name"],
                    powerup.config["color"], duration=120, float_speed=0, font_size=48
                )
                
                self.powerups.remove(powerup)
                return True
        return False
    
    def update(self, keys):
        if not self.game_started or self.paused:
            self.particle_system.update()
            return
        
        if self.game_over:
            self.particle_system.update()
            return
        
        if self.collision_happened and self.collision_delay > 0:
            self.collision_delay -= 1
            
            self.flash_timer += 1
            if self.flash_timer >= self.flash_interval:
                self.show_flash = not self.show_flash
                self.flash_timer = 0
            
            self.collision_particle_timer += 1
            if self.collision_particle_timer % 3 == 0:
                offset_x = random.randint(-30, 30)
                offset_y = random.randint(-30, 30)
                self.particle_system.create_collision(
                    self.collision_x + offset_x, 
                    self.collision_y + offset_y, 
                    random.randint(5, 15)
                )
            
            self.particle_system.update()
            self.text_manager.update()
            
            if self.collision_delay <= 0:
                self.game_over = True
                self.show_flash = False
            return
        
        if self.has_shield:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.has_shield = False
        
        if self.speed_boost:
            self.speed_boost_duration -= 1
            if self.speed_boost_duration <= 0:
                self.speed_boost = False
            self.ship.speed = self.base_speed * 1.8
        else:
            self.ship.speed = self.base_speed
        
        if self.meteor_slow:
            self.meteor_slow_duration -= 1
            if self.meteor_slow_duration <= 0:
                self.meteor_slow = False
        
        self.ship.update(keys)
        
        if self.ship.is_moving:
            engine_x, engine_y = self.ship.get_engine_position()
            self.particle_system.create_engine_trail(engine_x, engine_y, self.ship.direction)
        
        self.spawn_meteor()
        self.spawn_powerup()
        
        for meteor in self.meteors[:]:
            if self.meteor_slow and meteor.speed > 2:
                meteor.y += meteor.speed * 0.5
            else:
                meteor.update()
            
            if meteor.y > SCREEN_HEIGHT:
                meteor_center = meteor.get_center()
                self.particle_system.create_explosion(meteor_center[0], SCREEN_HEIGHT - 20, 12)
                self.meteors.remove(meteor)
                self.score += 10
                self.text_manager.add_score_text(80, 30, 10)
        
        for powerup in self.powerups[:]:
            if not powerup.update():
                self.powerups.remove(powerup)
        
        self.check_collisions()
        self.check_powerup_collisions()
        self.particle_system.update()
        self.text_manager.update()
        
        if self.warning_flash:
            self.warning_flash_timer += 1
            if self.warning_flash_timer >= self.warning_flash_duration:
                self.warning_flash = False
                self.warning_flash_timer = 0
    
    def draw_start_screen(self, surface, mouse_pos):
        surface.fill(BLACK)
        
        title_text = large_font.render("躲避陨石", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        surface.blit(title_text, title_rect)
        
        instruction_text1 = small_font.render("使用左右箭头键控制飞船", True, WHITE)
        instruction_rect1 = instruction_text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(instruction_text1, instruction_rect1)
        
        instruction_text2 = small_font.render("按 P 键暂停游戏", True, WHITE)
        instruction_rect2 = instruction_text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15))
        surface.blit(instruction_text2, instruction_rect2)
        
        self.start_button.draw(surface, mouse_pos)
    
    def draw_pause_screen(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        pause_text = large_font.render("游戏暂停", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        surface.blit(pause_text, pause_rect)
        
        self.pause_continue_button.draw(surface, mouse_pos)
        self.pause_quit_button.draw(surface, mouse_pos)
    
    def draw_game_over_screen(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        game_over_text = large_font.render("游戏结束!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(game_over_text, game_over_rect)
        
        final_score_text = medium_font.render(f"最终分数: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        surface.blit(final_score_text, final_score_rect)
        
        restart_hint = small_font.render("按 R 键重新开始 或 点击按钮", True, GRAY)
        restart_hint_rect = restart_hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        surface.blit(restart_hint, restart_hint_rect)
        
        self.game_over_restart_button.draw(surface, mouse_pos)
        self.game_over_quit_button.draw(surface, mouse_pos)
    
    def draw(self, surface, mouse_pos):
        surface.fill(BLACK)
        
        if not self.game_started:
            self.draw_start_screen(surface, mouse_pos)
            return
        
        self.particle_system.draw(surface)
        
        if not (self.collision_happened and self.collision_delay > 0):
            for powerup in self.powerups:
                powerup.draw(surface)
            
            for meteor in self.meteors:
                meteor.draw(surface)
            
            self.ship.draw(surface)
            
            if self.has_shield:
                ship_center_x = self.ship.x + self.ship.width // 2
                ship_center_y = self.ship.y + self.ship.height // 2
                
                shield_radius = max(self.ship.width, self.ship.height) // 2 + 20
                shield_pulse = 5 * math.sin(pygame.time.get_ticks() * 0.005)
                shield_radius += shield_pulse
                
                shield_alpha = 100 + int(50 * math.sin(pygame.time.get_ticks() * 0.008))
                
                shield_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(
                    shield_surface, 
                    (*self.shield_color, shield_alpha),
                    (ship_center_x, ship_center_y),
                    shield_radius,
                    3
                )
                surface.blit(shield_surface, (0, 0))
                
                pygame.draw.circle(
                    surface,
                    (*self.shield_color, 150),
                    (ship_center_x, ship_center_y),
                    shield_radius - 10,
                    2
                )
        
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))
        
        lives_text = font.render(f"生命: {self.lives}", True, RED if self.lives == 1 else GREEN)
        surface.blit(lives_text, (10, 50))
        
        effect_y = 90
        if self.has_shield:
            shield_remaining = self.shield_duration // FPS
            effect_text = small_font.render(f"护盾: {shield_remaining + 1}s", True, self.shield_color)
            surface.blit(effect_text, (10, effect_y))
            effect_y += 25
        
        if self.speed_boost:
            speed_remaining = self.speed_boost_duration // FPS
            effect_text = small_font.render(f"加速: {speed_remaining + 1}s", True, YELLOW)
            surface.blit(effect_text, (10, effect_y))
            effect_y += 25
        
        if self.meteor_slow:
            slow_remaining = self.meteor_slow_duration // FPS
            effect_text = small_font.render(f"减速: {slow_remaining + 1}s", True, POWERUP_CONFIG[POWERUP_SLOW]["color"])
            surface.blit(effect_text, (10, effect_y))
        
        pause_hint = small_font.render("按 P 暂停", True, GRAY)
        surface.blit(pause_hint, (SCREEN_WIDTH - 120, 10))
        
        self.text_manager.draw(surface)
        
        if self.warning_flash:
            flash_frame = self.warning_flash_timer // self.warning_flash_interval
            if flash_frame % 2 == 0:
                border_thickness = 15
                border_color = (255, 0, 0, 150)
                
                pygame.draw.rect(surface, border_color[:3], (0, 0, SCREEN_WIDTH, border_thickness))
                pygame.draw.rect(surface, border_color[:3], (0, SCREEN_HEIGHT - border_thickness, SCREEN_WIDTH, border_thickness))
                pygame.draw.rect(surface, border_color[:3], (0, 0, border_thickness, SCREEN_HEIGHT))
                pygame.draw.rect(surface, border_color[:3], (SCREEN_WIDTH - border_thickness, 0, border_thickness, SCREEN_HEIGHT))
        
        if self.collision_happened and self.collision_delay > 0:
            if self.show_flash:
                flash_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_overlay.fill((255, 50, 50, 100))
                surface.blit(flash_overlay, (0, 0))
            
            remaining_seconds = max(0, self.collision_delay // FPS)
            countdown_text = large_font.render(f"{remaining_seconds + 1}", True, RED)
            countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(countdown_text, countdown_rect)
            
            collision_hint = small_font.render("碰撞!", True, YELLOW)
            collision_hint_rect = collision_hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            surface.blit(collision_hint, collision_hint_rect)
        
        if self.paused:
            self.draw_pause_screen(surface, mouse_pos)
        elif self.game_over:
            self.draw_game_over_screen(surface, mouse_pos)

def main():
    game = Game()
    
    mouse_clicked = False
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if game.game_over:
                        game.reset()
                elif event.key == pygame.K_p:
                    if game.game_started and not game.game_over:
                        game.paused = not game.paused
                elif event.key == pygame.K_ESCAPE:
                    if game.paused:
                        game.paused = False
        
        if not game.game_started:
            if game.start_button.is_clicked(mouse_pos, mouse_clicked):
                game.reset()
        elif game.paused:
            if game.pause_continue_button.is_clicked(mouse_pos, mouse_clicked):
                game.paused = False
            if game.pause_quit_button.is_clicked(mouse_pos, mouse_clicked):
                running = False
        elif game.game_over:
            if game.game_over_restart_button.is_clicked(mouse_pos, mouse_clicked):
                game.reset()
            if game.game_over_quit_button.is_clicked(mouse_pos, mouse_clicked):
                running = False
        
        keys = pygame.key.get_pressed()
        game.update(keys)
        game.draw(screen, mouse_pos)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
