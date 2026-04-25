import random
import math
import pygame
import sys

from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, BLACK, RED, GREEN, YELLOW, GRAY,
    POWERUP_SHIELD, POWERUP_SPEED, POWERUP_SLOW, POWERUP_SCORE,
    POWERUP_CONFIG
)
from game.core.utils import get_font, get_large_font, get_medium_font, get_small_font
from game.entities.particle import ParticleSystem
from game.entities.ship import Ship
from game.entities.meteor import Meteor
from game.entities.powerup import PowerUp
from game.ui.button import Button
from game.ui.floating_text import FloatingTextManager

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
        
        title_text = get_large_font().render("躲避陨石", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        surface.blit(title_text, title_rect)
        
        instruction_text1 = get_small_font().render("使用左右箭头键控制飞船", True, WHITE)
        instruction_rect1 = instruction_text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(instruction_text1, instruction_rect1)
        
        instruction_text2 = get_small_font().render("按 P 键暂停游戏", True, WHITE)
        instruction_rect2 = instruction_text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15))
        surface.blit(instruction_text2, instruction_rect2)
        
        self.start_button.draw(surface, mouse_pos)
    
    def draw_pause_screen(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        pause_text = get_large_font().render("游戏暂停", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        surface.blit(pause_text, pause_rect)
        
        self.pause_continue_button.draw(surface, mouse_pos)
        self.pause_quit_button.draw(surface, mouse_pos)
    
    def draw_game_over_screen(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        game_over_text = get_large_font().render("游戏结束!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(game_over_text, game_over_rect)
        
        final_score_text = get_medium_font().render(f"最终分数: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        surface.blit(final_score_text, final_score_rect)
        
        restart_hint = get_small_font().render("按 R 键重新开始 或 点击按钮", True, GRAY)
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
        
        score_text = get_font().render(f"分数: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))
        
        lives_text = get_font().render(f"生命: {self.lives}", True, RED if self.lives == 1 else GREEN)
        surface.blit(lives_text, (10, 50))
        
        effect_y = 90
        if self.has_shield:
            shield_remaining = self.shield_duration // FPS
            effect_text = get_small_font().render(f"护盾: {shield_remaining + 1}s", True, self.shield_color)
            surface.blit(effect_text, (10, effect_y))
            effect_y += 25
        
        if self.speed_boost:
            speed_remaining = self.speed_boost_duration // FPS
            effect_text = get_small_font().render(f"加速: {speed_remaining + 1}s", True, YELLOW)
            surface.blit(effect_text, (10, effect_y))
            effect_y += 25
        
        if self.meteor_slow:
            slow_remaining = self.meteor_slow_duration // FPS
            effect_text = get_small_font().render(f"减速: {slow_remaining + 1}s", True, POWERUP_CONFIG[POWERUP_SLOW]["color"])
            surface.blit(effect_text, (10, effect_y))
        
        pause_hint = get_small_font().render("按 P 暂停", True, GRAY)
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
            countdown_text = get_large_font().render(f"{remaining_seconds + 1}", True, RED)
            countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(countdown_text, countdown_rect)
            
            collision_hint = get_small_font().render("碰撞!", True, YELLOW)
            collision_hint_rect = collision_hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            surface.blit(collision_hint, collision_hint_rect)
        
        if self.paused:
            self.draw_pause_screen(surface, mouse_pos)
        elif self.game_over:
            self.draw_game_over_screen(surface, mouse_pos)
