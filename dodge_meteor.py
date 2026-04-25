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

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
    
    def draw(self, surface, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
        
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
        self.particle_system = ParticleSystem()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.meteor_timer = 0
        self.meteor_interval = 60
        self.game_started = False
        self.collision_happened = False
        
        self.collision_delay = 0
        self.collision_delay_frames = FPS * 5
        self.flash_timer = 0
        self.flash_interval = 5
        self.show_flash = False
        self.collision_particle_timer = 0
        self.collision_x = 0
        self.collision_y = 0
        
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
        self.particle_system = ParticleSystem()
        self.score = 0
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
    
    def spawn_meteor(self):
        self.meteor_timer += 1
        if self.meteor_timer >= self.meteor_interval:
            self.meteors.append(Meteor())
            self.meteor_timer = 0
            if self.meteor_interval > 20:
                self.meteor_interval -= 0.5
    
    def check_collisions(self):
        for meteor in self.meteors:
            if self.ship.rect.colliderect(meteor.rect):
                if not self.collision_happened:
                    ship_center = (self.ship.x + self.ship.width // 2, 
                                   self.ship.y + self.ship.height // 2)
                    self.particle_system.create_collision(ship_center[0], ship_center[1], 50)
                    meteor_center = meteor.get_center()
                    self.particle_system.create_collision(meteor_center[0], meteor_center[1], 35)
                    
                    self.collision_x = (ship_center[0] + meteor_center[0]) // 2
                    self.collision_y = (ship_center[1] + meteor_center[1]) // 2
                    
                    self.collision_happened = True
                    self.collision_delay = self.collision_delay_frames
                    self.flash_timer = 0
                    self.collision_particle_timer = 0
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
            
            if self.collision_delay <= 0:
                self.game_over = True
                self.show_flash = False
            return
        
        self.ship.update(keys)
        
        if self.ship.is_moving:
            engine_x, engine_y = self.ship.get_engine_position()
            self.particle_system.create_engine_trail(engine_x, engine_y, self.ship.direction)
        
        self.spawn_meteor()
        
        for meteor in self.meteors[:]:
            meteor.update()
            if meteor.y > SCREEN_HEIGHT:
                meteor_center = meteor.get_center()
                self.particle_system.create_explosion(meteor_center[0], SCREEN_HEIGHT - 20, 12)
                self.meteors.remove(meteor)
                self.score += 10
        
        self.check_collisions()
        self.particle_system.update()
    
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
            for meteor in self.meteors:
                meteor.draw(surface)
            
            self.ship.draw(surface)
        
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))
        
        pause_hint = small_font.render("按 P 暂停", True, GRAY)
        surface.blit(pause_hint, (SCREEN_WIDTH - 120, 10))
        
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
