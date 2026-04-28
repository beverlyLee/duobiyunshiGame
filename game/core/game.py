import random
import math
import pygame
import sys

from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, BLACK, RED, GREEN, YELLOW, GRAY,
    POWERUP_SHIELD, POWERUP_BULLET, POWERUP_SLOW,
    POWERUP_CONFIG, SHIELD_BLUE, BULLET_YELLOW, SLOW_GREEN,
    METEOR_CONFIG, METEOR_SPLIT,
    METEOR_TRACKER, METEOR_EXPLOSIVE, METEOR_ARMORED,
    SPECIAL_METEOR_CONFIG
)
from game.core.utils import get_font, get_large_font, get_medium_font, get_small_font
from game.core.audio_manager import AudioManager, SoundType, get_audio_manager
from game.entities.particle import ParticleSystem
from game.entities.ship import Ship
from game.entities.meteor import Meteor
from game.entities.powerup import PowerUp
from game.entities.bullet import Bullet
from game.entities.starfield import StarField
from game.ui.button import Button
from game.ui.floating_text import FloatingTextManager

try:
    from game.core.screen_shake import ScreenShake, ShakeType
    from game.core.combo_system import ComboSystem, DifficultySystem
    HAS_ADVANCED_SYSTEMS = True
except ImportError:
    HAS_ADVANCED_SYSTEMS = False

class Game:
    def __init__(self):
        self.ship = Ship()
        self.meteors = []
        self.powerups = []
        self.bullets = []
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
        
        self.special_meteor_counters = {
            METEOR_TRACKER: 0,
            METEOR_ARMORED: 0,
            METEOR_EXPLOSIVE: 0,
        }
        self.current_level = 1
        self.last_checked_level = 1
        
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
        self.shield_flash_timer = 0
        self.shield_flash_interval = 8
        self.show_shield_outline = True
        self.shield_color = SHIELD_BLUE
        
        self.has_bullet = False
        self.bullet_duration = 0
        self.bullet_cooldown = 0
        self.bullet_cooldown_frames = 3
        
        self.meteor_slow = False
        self.meteor_slow_duration = 0
        
        self.move_sound_cooldown = 0
        self.move_sound_interval = 8
        
        self.starfield = StarField()
        
        if HAS_ADVANCED_SYSTEMS:
            self.screen_shake = ScreenShake()
            self.combo_system = ComboSystem()
            self.difficulty_system = DifficultySystem()
        else:
            self.screen_shake = None
            self.combo_system = None
            self.difficulty_system = None
        
        self.render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_angle = 0
        
        self.start_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80,
            200, 50, "开始游戏", GREEN, (0, 200, 0)
        )
        
        self.pause_continue_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20,
            200, 50, "继续游戏", GREEN, (0, 200, 0)
        )
        self.pause_quit_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 90,
            200, 50, "退出游戏", RED, (200, 0, 0)
        )
        
        self.game_over_restart_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 130,
            200, 50, "重新开始", GREEN, (0, 200, 0)
        )
        self.game_over_quit_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 210,
            200, 50, "退出游戏", RED, (200, 0, 0)
        )
        
        self.high_score = 0
        self._load_high_score()
        
        self.audio_manager = get_audio_manager()
        self.audio_manager.load_all_sounds()
    
    def _load_high_score(self):
        try:
            with open("high_score.txt", "r") as f:
                self.high_score = int(f.read().strip())
        except:
            self.high_score = 0
    
    def _save_high_score(self):
        try:
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def reset(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
        
        self.ship = Ship()
        self.meteors = []
        self.powerups = []
        self.bullets = []
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
        
        self.special_meteor_counters = {
            METEOR_TRACKER: 0,
            METEOR_ARMORED: 0,
            METEOR_EXPLOSIVE: 0,
        }
        self.current_level = 1
        self.last_checked_level = 1
        
        self.collision_delay = 0
        self.flash_timer = 0
        self.show_flash = False
        self.collision_particle_timer = 0
        
        self.warning_flash = False
        self.warning_flash_timer = 0
        
        self.powerup_timer = 0
        
        self.has_shield = False
        self.shield_duration = 0
        self.shield_flash_timer = 0
        self.show_shield_outline = True
        
        self.has_bullet = False
        self.bullet_duration = 0
        self.bullet_cooldown = 0
        
        self.meteor_slow = False
        self.meteor_slow_duration = 0
        
        self.move_sound_cooldown = 0
        
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_angle = 0
        
        if self.screen_shake:
            self.screen_shake.stop_shake()
        
        if self.combo_system:
            self.combo_system = ComboSystem()
        
        if self.difficulty_system:
            self.difficulty_system = DifficultySystem()
        
        self.audio_manager.play_music("background")
    
    def add_score_with_combo(self, base_score, source=""):
        if self.combo_system:
            multiplier = self.combo_system.add_hit(1)
            final_score = int(base_score * multiplier)
            self.score += final_score
            
            if multiplier > 1.0:
                self.text_manager.add_score_text(80, 30, final_score)
            else:
                self.text_manager.add_score_text(80, 30, base_score)
        else:
            self.score += base_score
            self.text_manager.add_score_text(80, 30, base_score)
    
    def reset_combo(self):
        if self.combo_system:
            self.combo_system.reset_combo()
    
    def trigger_shake(self, shake_type):
        if self.screen_shake and shake_type:
            self.screen_shake.add_trauma(shake_type.get("trauma", 0.3))
    
    def shoot_bullet(self):
        if self.has_bullet and self.bullet_cooldown <= 0:
            ship_center_x = self.ship.x + self.ship.width // 2
            ship_top_y = self.ship.y
            self.bullets.append(Bullet(ship_center_x, ship_top_y))
            self.bullet_cooldown = self.bullet_cooldown_frames
            self.audio_manager.play_sound(SoundType.SHOOT)
    
    def _update_level_and_counters(self):
        if self.difficulty_system:
            self.current_level = self.difficulty_system.get_level()
            
            if self.current_level != self.last_checked_level:
                self.last_checked_level = self.current_level
                for meteor_type in self.special_meteor_counters:
                    self.special_meteor_counters[meteor_type] = 0
    
    def _can_spawn_special_meteor(self, meteor_type):
        if not self.difficulty_system:
            return False
        
        special_config = SPECIAL_METEOR_CONFIG.get(meteor_type)
        if not special_config:
            return False
        
        if self.current_level < special_config["min_level"]:
            return False
        
        count = self.special_meteor_counters.get(meteor_type, 0)
        max_count = random.randint(special_config["per_level_min"], special_config["per_level_max"])
        
        return count < max_count
    
    def _spawn_special_meteor(self, meteor_type):
        if meteor_type == METEOR_TRACKER:
            special_config = SPECIAL_METEOR_CONFIG.get(METEOR_TRACKER)
            colors = special_config.get("colors", [])
            color_override = random.choice(colors) if colors else None
            new_meteor = Meteor(meteor_type=METEOR_TRACKER, ship=self.ship, color_override=color_override)
        else:
            new_meteor = Meteor(meteor_type=meteor_type, ship=self.ship)
        
        self.meteors.append(new_meteor)
        self.special_meteor_counters[meteor_type] = self.special_meteor_counters.get(meteor_type, 0) + 1
        
        return new_meteor
    
    def spawn_meteor(self):
        self.meteor_timer += 1
        
        effective_interval = self.meteor_interval
        if self.difficulty_system:
            effective_interval = int(self.meteor_interval / self.difficulty_system.get_meteor_spawn_multiplier())
        
        if self.meteor_timer >= effective_interval:
            self._update_level_and_counters()
            
            available_special = []
            for meteor_type in [METEOR_TRACKER, METEOR_ARMORED, METEOR_EXPLOSIVE]:
                if self._can_spawn_special_meteor(meteor_type):
                    available_special.append(meteor_type)
            
            if available_special and random.random() < 0.25:
                special_type = random.choice(available_special)
                self._spawn_special_meteor(special_type)
            else:
                new_meteor = Meteor(ship=self.ship)
                self.meteors.append(new_meteor)
            
            self.meteor_timer = 0
            if self.meteor_interval > 20:
                self.meteor_interval -= 0.5
    
    def spawn_powerup(self):
        self.powerup_timer += 1
        if self.powerup_timer >= self.powerup_interval:
            self.powerups.append(PowerUp())
            self.powerup_timer = 0
            self.powerup_interval = FPS * random.randint(3, 6)
    
    def create_explosion_chain(self, source_meteor):
        explosion_center = source_meteor.get_center()
        explosion_radius = source_meteor.get_explosion_radius()
        
        self.particle_system.create_large_explosion(
            explosion_center[0], explosion_center[1], explosion_radius
        )
        
        if self.screen_shake:
            self.screen_shake.add_trauma(0.6)
        
        for meteor in self.meteors[:]:
            if meteor is source_meteor:
                continue
            
            meteor_center = meteor.get_center()
            dx = explosion_center[0] - meteor_center[0]
            dy = explosion_center[1] - meteor_center[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= explosion_radius:
                damage = source_meteor.explosion_damage
                if meteor.take_damage(damage):
                    self.particle_system.create_explosion(
                        meteor_center[0], meteor_center[1], 20
                    )
                    
                    if meteor.can_split():
                        split_meteors = meteor.get_split_meteors()
                        for split_meteor in split_meteors:
                            split_center = split_meteor.get_center()
                            self.particle_system.create_explosion(
                                split_center[0], split_center[1], 5
                            )
                            self.meteors.append(split_meteor)
                    
                    if meteor.should_explode_on_destroy():
                        self.create_explosion_chain(meteor)
                    
                    score_value = meteor.config.get("score", 10)
                    self.add_score_with_combo(score_value, "explosion_destroy")
                    self.meteors.remove(meteor)
    
    def check_bullet_collisions(self):
        for bullet in self.bullets[:]:
            for meteor in self.meteors[:]:
                if bullet.rect.colliderect(meteor.rect):
                    meteor_center = meteor.get_center()
                    
                    self.particle_system.create_explosion(
                        meteor_center[0], meteor_center[1], 8
                    )
                    
                    if self.screen_shake:
                        self.screen_shake.add_trauma(0.15)
                    
                    if meteor.is_explosive():
                        meteor.activate_fuse()
                    
                    if meteor.take_damage(2):
                        if meteor.should_explode_on_destroy():
                            self.create_explosion_chain(meteor)
                        else:
                            self.particle_system.create_explosion(
                                meteor_center[0], meteor_center[1], 25
                            )
                            
                            if self.screen_shake:
                                self.screen_shake.add_trauma(0.3)
                            
                            if meteor.can_split():
                                split_meteors = meteor.get_split_meteors()
                                for split_meteor in split_meteors:
                                    split_center = split_meteor.get_center()
                                    self.particle_system.create_explosion(
                                        split_center[0], split_center[1], 5
                                    )
                                    self.meteors.append(split_meteor)
                            
                            score_value = meteor.config.get("score", 10)
                            self.add_score_with_combo(score_value, "destroy")
                        
                        if meteor in self.meteors:
                            self.meteors.remove(meteor)
                        self.audio_manager.play_sound(SoundType.EXPLOSION)
                    else:
                        self.audio_manager.play_sound(SoundType.HIT)
                    
                    self.bullets.remove(bullet)
                    break
    
    def check_collisions(self):
        for meteor in self.meteors[:]:
            if self.ship.rect.colliderect(meteor.rect):
                ship_center = (self.ship.x + self.ship.width // 2, 
                               self.ship.y + self.ship.height // 2)
                meteor_center = meteor.get_center()
                
                if self.has_shield:
                    self.particle_system.create_collision(meteor_center[0], meteor_center[1], 25)
                    
                    if self.screen_shake:
                        self.screen_shake.add_trauma(0.25)
                    
                    if meteor.is_explosive():
                        meteor.activate_fuse()
                    
                    if meteor.take_damage():
                        if meteor.should_explode_on_destroy():
                            self.create_explosion_chain(meteor)
                        else:
                            self.particle_system.create_explosion(
                                meteor_center[0], meteor_center[1], 25
                            )
                            
                            if meteor.can_split():
                                split_meteors = meteor.get_split_meteors()
                                for split_meteor in split_meteors:
                                    split_center = split_meteor.get_center()
                                    self.particle_system.create_explosion(
                                        split_center[0], split_center[1], 5
                                    )
                                    self.meteors.append(split_meteor)
                            
                            score_value = meteor.config.get("score", 10)
                            self.add_score_with_combo(score_value, "shield_destroy")
                        
                        if meteor in self.meteors:
                            self.meteors.remove(meteor)
                        self.audio_manager.play_sound(SoundType.EXPLOSION)
                    else:
                        self.audio_manager.play_sound(SoundType.HIT)
                    
                    if meteor in self.meteors:
                        self.meteors.remove(meteor)
                    continue
                
                if not self.collision_happened:
                    self.particle_system.create_collision(ship_center[0], ship_center[1], 50)
                    self.particle_system.create_collision(meteor_center[0], meteor_center[1], 35)
                    
                    if self.screen_shake:
                        self.screen_shake.add_trauma(0.7)
                    
                    if meteor.is_explosive():
                        meteor.activate_fuse()
                    
                    if meteor.take_damage():
                        if meteor.should_explode_on_destroy():
                            self.create_explosion_chain(meteor)
                        else:
                            if meteor.can_split():
                                split_meteors = meteor.get_split_meteors()
                                for split_meteor in split_meteors:
                                    split_center = split_meteor.get_center()
                                    self.particle_system.create_explosion(
                                        split_center[0], split_center[1], 5
                                    )
                                    self.meteors.append(split_meteor)
                    
                    if meteor in self.meteors:
                        self.meteors.remove(meteor)
                    
                    self.reset_combo()
                    
                    self.collision_x = (ship_center[0] + meteor_center[0]) // 2
                    self.collision_y = (ship_center[1] + meteor_center[1]) // 2
                    
                    self.lives -= 1
                    
                    self.audio_manager.play_sound(SoundType.COLLISION)
                    
                    if self.lives <= 0:
                        self.collision_happened = True
                        self.collision_delay = self.collision_delay_frames
                        self.flash_timer = 0
                        self.collision_particle_timer = 0
                        self.audio_manager.play_sound(SoundType.GAME_OVER)
                    else:
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
                
                if self.screen_shake:
                    self.screen_shake.add_trauma(0.1)
                
                if powerup.type == POWERUP_SHIELD:
                    self.has_shield = True
                    self.shield_duration = powerup.config["duration"]
                    self.shield_flash_timer = 0
                    self.show_shield_outline = True
                elif powerup.type == POWERUP_BULLET:
                    self.has_bullet = True
                    self.bullet_duration = powerup.config["duration"]
                    self.bullet_cooldown = 0
                elif powerup.type == POWERUP_SLOW:
                    self.meteor_slow = True
                    self.meteor_slow_duration = powerup.config["duration"]
                
                self.text_manager.add_text(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                    powerup.config["name"],
                    powerup.config["color"], duration=120, float_speed=0, font_size=48
                )
                
                self.audio_manager.play_sound(SoundType.POWERUP)
                
                self.powerups.remove(powerup)
                return True
        return False
    
    def update(self, keys):
        if self.starfield:
            self.starfield.update()
        
        if self.screen_shake:
            self.shake_offset_x, self.shake_offset_y, self.shake_angle = self.screen_shake.update()
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
            self.shake_angle = 0
        
        if self.combo_system:
            self.combo_system.update()
        
        if self.difficulty_system:
            self.difficulty_system.update(self.score)
            if self.difficulty_system.has_just_leveled_up():
                self.audio_manager.play_sound(SoundType.LEVEL_UP)
        
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
                self.audio_manager.stop_music()
                
                if self.score > self.high_score:
                    self.high_score = self.score
                    self._save_high_score()
            return
        
        if self.has_shield:
            self.shield_duration -= 1
            self.shield_flash_timer += 1
            if self.shield_flash_timer >= self.shield_flash_interval:
                self.show_shield_outline = not self.show_shield_outline
                self.shield_flash_timer = 0
            if self.shield_duration <= 0:
                self.has_shield = False
                self.show_shield_outline = True
        
        if self.has_bullet:
            self.bullet_duration -= 1
            if self.bullet_cooldown > 0:
                self.bullet_cooldown -= 1
            if self.bullet_duration <= 0:
                self.has_bullet = False
                self.bullet_cooldown = 0
        
        if self.meteor_slow:
            self.meteor_slow_duration -= 1
            if self.meteor_slow_duration <= 0:
                self.meteor_slow = False
        
        self.ship.update(keys)
        
        if self.ship.is_moving:
            engine_x, engine_y = self.ship.get_engine_position()
            self.particle_system.create_engine_trail(engine_x, engine_y, self.ship.direction)
            
            if self.move_sound_cooldown <= 0:
                self.audio_manager.play_sound(SoundType.MOVE)
                self.move_sound_cooldown = self.move_sound_interval
            
            self.shoot_bullet()
        else:
            self.move_sound_cooldown = 0
        
        if self.move_sound_cooldown > 0:
            self.move_sound_cooldown -= 1
        
        self.spawn_meteor()
        self.spawn_powerup()
        
        for bullet in self.bullets[:]:
            if not bullet.update():
                self.bullets.remove(bullet)
        
        for meteor in self.meteors[:]:
            speed_multiplier = 1.0
            if self.difficulty_system:
                speed_multiplier = self.difficulty_system.get_meteor_speed_multiplier()
            
            if self.meteor_slow and meteor.speed > 2:
                meteor.y += meteor.speed * 0.5 * speed_multiplier
                meteor.rect.y = meteor.y
            else:
                meteor.y += meteor.speed * speed_multiplier
                meteor.rect.y = meteor.y
                meteor.update()
            
            if meteor.is_explosive() and meteor.update_explosive():
                self.create_explosion_chain(meteor)
                if meteor in self.meteors:
                    self.meteors.remove(meteor)
                self.audio_manager.play_sound(SoundType.EXPLOSION)
                continue
            
            if meteor.y > SCREEN_HEIGHT:
                meteor_center = meteor.get_center()
                self.particle_system.create_explosion(meteor_center[0], SCREEN_HEIGHT - 20, 12)
                self.meteors.remove(meteor)
                
                score_value = meteor.config.get("score", 10)
                self.add_score_with_combo(score_value, "dodge")
                self.audio_manager.play_sound(SoundType.DODGE)
        
        for powerup in self.powerups[:]:
            if not powerup.update():
                self.powerups.remove(powerup)
        
        self.check_bullet_collisions()
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
        self.starfield.draw(surface)
        
        title_text = get_large_font().render("躲避陨石", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180))
        
        glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(5, 0, -1):
            alpha = 20 + i * 10
            offset = i * 2
            temp_surf = get_large_font().render("躲避陨石", True, (*YELLOW, alpha))
            temp_rect = temp_surf.get_rect(center=(SCREEN_WIDTH // 2 + offset, SCREEN_HEIGHT // 2 - 180 + offset))
            glow_surface.blit(temp_surf, temp_rect)
        
        surface.blit(glow_surface, (0, 0))
        surface.blit(title_text, title_rect)
        
        if self.high_score > 0:
            high_score_text = get_font().render(f"最高分: {self.high_score}", True, (255, 215, 0))
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 110))
            surface.blit(high_score_text, high_score_rect)
        
        instruction_text1 = get_small_font().render("使用左右箭头键控制飞船", True, WHITE)
        instruction_rect1 = instruction_text1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(instruction_text1, instruction_rect1)
        
        instruction_text2 = get_small_font().render("按空格发射子弹", True, WHITE)
        instruction_rect2 = instruction_text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15))
        surface.blit(instruction_text2, instruction_rect2)
        
        instruction_text3 = get_small_font().render("按 P 键暂停游戏", True, WHITE)
        instruction_rect3 = instruction_text3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        surface.blit(instruction_text3, instruction_rect3)
        
        self.start_button.draw(surface, mouse_pos)
    
    def draw_pause_screen(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        pause_text = get_large_font().render("游戏暂停", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(pause_text, pause_rect)
        
        current_score_text = get_medium_font().render(f"当前分数: {self.score}", True, WHITE)
        current_score_rect = current_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        surface.blit(current_score_text, current_score_rect)
        
        self.pause_continue_button.draw(surface, mouse_pos)
        self.pause_quit_button.draw(surface, mouse_pos)
    
    def draw_game_over_screen(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255))
        surface.blit(overlay, (0, 0))
        
        game_over_text = get_large_font().render("游戏结束!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180))
        surface.blit(game_over_text, game_over_rect)
        
        final_score_text = get_medium_font().render(f"最终分数: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        surface.blit(final_score_text, final_score_rect)
        
        current_y = SCREEN_HEIGHT // 2 - 60
        
        if self.score == self.high_score and self.score > 0:
            new_record_text = get_font().render("新纪录!", True, (255, 215, 0))
            new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH // 2, current_y))
            surface.blit(new_record_text, new_record_rect)
            current_y += 45
        
        high_score_text = get_font().render(f"最高分: {self.high_score}", True, (255, 215, 0))
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, current_y))
        surface.blit(high_score_text, high_score_rect)
        current_y += 45
        
        if self.combo_system:
            max_combo_text = get_font().render(f"最高连击: {self.combo_system.get_max_combo()}", True, (255, 150, 150))
            max_combo_rect = max_combo_text.get_rect(center=(SCREEN_WIDTH // 2, current_y))
            surface.blit(max_combo_text, max_combo_rect)
            current_y += 50
        
        restart_hint = get_small_font().render("按 R 键重新开始 或 点击按钮", True, GRAY)
        restart_hint_rect = restart_hint.get_rect(center=(SCREEN_WIDTH // 2, current_y))
        surface.blit(restart_hint, restart_hint_rect)
        
        self.game_over_restart_button.draw(surface, mouse_pos)
        self.game_over_quit_button.draw(surface, mouse_pos)
    
    def draw_powerup_status(self, surface):
        status_x = 10
        status_y = 90
        status_width = 200
        status_height = 35
        status_spacing = 45
        
        active_powerups = []
        
        if self.has_shield:
            active_powerups.append({
                "type": "shield",
                "duration": self.shield_duration,
                "color": SHIELD_BLUE,
                "name": "护盾",
                "icon": "🛡️"
            })
        
        if self.has_bullet:
            active_powerups.append({
                "type": "bullet",
                "duration": self.bullet_duration,
                "color": BULLET_YELLOW,
                "name": "子弹",
                "icon": "⚡"
            })
        
        if self.meteor_slow:
            active_powerups.append({
                "type": "slow",
                "duration": self.meteor_slow_duration,
                "color": SLOW_GREEN,
                "name": "减速",
                "icon": "⏱️"
            })
        
        for i, powerup in enumerate(active_powerups):
            current_y = status_y + i * status_spacing
            
            bg_surface = pygame.Surface((status_width, status_height), pygame.SRCALPHA)
            bg_surface.fill((*powerup["color"], 80))
            pygame.draw.rect(bg_surface, (*powerup["color"], 180), (0, 0, status_width, status_height), 2)
            surface.blit(bg_surface, (status_x, current_y))
            
            icon_text = get_small_font().render(powerup["icon"], True, WHITE)
            icon_rect = icon_text.get_rect(midleft=(status_x + 15, current_y + status_height // 2))
            surface.blit(icon_text, icon_rect)
            
            seconds_remaining = max(0, (powerup["duration"] + FPS - 1) // FPS)
            time_text = get_small_font().render(f"{seconds_remaining}s", True, WHITE)
            time_rect = time_text.get_rect(midright=(status_x + status_width - 10, current_y + status_height // 2))
            surface.blit(time_text, time_rect)
            
            progress_width = status_width - 60
            progress_x = status_x + 40
            progress_y = current_y + status_height - 8
            
            max_duration = POWERUP_CONFIG[POWERUP_SHIELD]["duration"] if powerup["type"] == "shield" else \
                          POWERUP_CONFIG[POWERUP_BULLET]["duration"] if powerup["type"] == "bullet" else \
                          POWERUP_CONFIG[POWERUP_SLOW]["duration"]
            
            progress = powerup["duration"] / max_duration
            current_progress_width = int(progress_width * progress)
            
            pygame.draw.rect(surface, (50, 50, 50), (progress_x, progress_y, progress_width, 4))
            if current_progress_width > 0:
                pygame.draw.rect(surface, powerup["color"], (progress_x, progress_y, current_progress_width, 4))
    
    def draw_ship_with_shield(self, surface):
        self.ship.draw(surface)
        
        if self.has_shield and self.show_shield_outline:
            ship_center_x = self.ship.x + self.ship.width // 2
            ship_center_y = self.ship.y + self.ship.height // 2
            
            shield_radius = max(self.ship.width, self.ship.height) // 2 + 15
            
            shield_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            pygame.draw.polygon(
                shield_surface, 
                (*self.shield_color, 200),
                [
                    (ship_center_x, self.ship.y - 8),
                    (self.ship.x - 8, self.ship.y + self.ship.height + 8),
                    (self.ship.x + self.ship.width + 8, self.ship.y + self.ship.height + 8)
                ],
                3
            )
            
            pygame.draw.circle(
                shield_surface,
                (*self.shield_color, 100),
                (ship_center_x, ship_center_y),
                shield_radius,
                2
            )
            
            surface.blit(shield_surface, (0, 0))
    
    def draw_game_ui(self, surface):
        score_text = get_font().render(f"分数: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))
        
        lives_text = get_font().render(f"生命: {self.lives}", True, RED if self.lives == 1 else GREEN)
        surface.blit(lives_text, (10, 50))
        
        if self.difficulty_system:
            level_text = get_small_font().render(f"等级: {self.difficulty_system.get_level()}", True, (200, 200, 100))
            surface.blit(level_text, (SCREEN_WIDTH - 120, 50))
        
        self.draw_powerup_status(surface)
        
        if self.has_bullet:
            bullet_hint = get_small_font().render("按空格发射子弹", True, BULLET_YELLOW)
            bullet_hint_rect = bullet_hint.get_rect(center=(SCREEN_WIDTH // 2, 15))
            surface.blit(bullet_hint, bullet_hint_rect)
        
        if self.combo_system and self.combo_system.get_combo() > 0:
            self.combo_system.draw(surface, SCREEN_WIDTH - 100, 120)
        
        pause_hint = get_small_font().render("按 P 暂停", True, GRAY)
        surface.blit(pause_hint, (SCREEN_WIDTH - 120, 10))
        
        self.text_manager.draw(surface)
    
    def draw_warning_effects(self, surface):
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
    
    def draw_difficulty_level_up(self, surface):
        if self.difficulty_system and self.difficulty_system.should_display_level_up():
            self.difficulty_system.draw_level_up(surface, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    def draw(self, surface, mouse_pos):
        if self.shake_offset_x != 0 or self.shake_offset_y != 0:
            draw_surface = self.render_surface
            draw_surface.fill(BLACK)
        else:
            draw_surface = surface
        
        if self.starfield:
            self.starfield.draw(draw_surface)
        
        if not self.game_started:
            self.draw_start_screen(draw_surface, mouse_pos)
        elif self.game_over:
            self.draw_game_over_screen(draw_surface, mouse_pos)
        else:
            self.particle_system.draw(draw_surface)
            
            if not (self.collision_happened and self.collision_delay > 0):
                for powerup in self.powerups:
                    powerup.draw(draw_surface)
                
                for meteor in self.meteors:
                    meteor.draw(draw_surface)
                
                for bullet in self.bullets:
                    bullet.draw(draw_surface)
                
                if self.has_shield:
                    self.draw_ship_with_shield(draw_surface)
                else:
                    self.ship.draw(draw_surface)
            
            self.draw_game_ui(draw_surface)
            self.draw_warning_effects(draw_surface)
            self.draw_difficulty_level_up(draw_surface)
            
            if self.paused:
                self.draw_pause_screen(draw_surface, mouse_pos)
        
        if (self.shake_offset_x != 0 or self.shake_offset_y != 0 or self.shake_angle != 0) and draw_surface is not surface:
            if abs(self.shake_angle) > 0.01:
                rotated_surface = pygame.transform.rotate(draw_surface, self.shake_angle)
                rotated_rect = rotated_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                surface.blit(rotated_surface, (rotated_rect.x + self.shake_offset_x, rotated_rect.y + self.shake_offset_y))
            else:
                surface.blit(draw_surface, (int(self.shake_offset_x), int(self.shake_offset_y)))
