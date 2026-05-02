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
    SPECIAL_METEOR_CONFIG,
    SYNERGY_CONFIG,
    ULTIMATE_GOLD, ULTIMATE_LIGHT_GOLD,
    ENERGY_SHIELD_PURPLE, ENERGY_SHIELD_LIGHT_PURPLE,
    HIGH_COMBO_THRESHOLD
)
from game.core.utils import get_font, get_large_font, get_medium_font, get_small_font
from game.core.audio_manager import AudioManager, SoundType, get_audio_manager
from game.core.skill_tree import get_skill_tree_manager, SkillTreeManager
from game.core.daily_challenge import (
    DailyChallenge, DailyChallengeManager, get_daily_challenge_manager,
    ModifierType, MODIFIER_CONFIG, RewardType, REWARD_CONFIG
)
from game.core.modifier_applier import ModifierApplier, get_modifier_applier
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
    from game.core.post_processing import PostProcessor
    HAS_ADVANCED_SYSTEMS = True
    HAS_POST_PROCESSING = True
except ImportError:
    HAS_ADVANCED_SYSTEMS = False
    HAS_POST_PROCESSING = False

class Game:
    def __init__(self):
        self.skill_tree = get_skill_tree_manager()
        
        self.ship = Ship()
        self.meteors = []
        self.powerups = []
        self.bullets = []
        self.particle_system = ParticleSystem()
        self.text_manager = FloatingTextManager()
        self.score = 0
        self.lives = 3
        self.max_lives = 3 + self.skill_tree.get_total_max_life()
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
        self.base_bullet_cooldown_frames = 3
        self.bullet_cooldown_frames = max(1, self.base_bullet_cooldown_frames - self.skill_tree.get_fire_rate_reduction())
        
        self.meteor_slow = False
        self.meteor_slow_duration = 0
        
        self.has_energy_shield = False
        self.has_ultimate_mode = False
        self.ultimate_duration = 0
        
        self.ultimate_transition_in = False
        self.ultimate_transition_out = False
        self.ultimate_transition_timer = 0
        self.ultimate_transition_max = 45
        
        self.visual_effect_phase = 0
        
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
        
        if HAS_POST_PROCESSING:
            self.post_processor = PostProcessor()
        else:
            self.post_processor = None
        
        self.prev_ship_position = None
        self.ship_speed = 0
        
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
        
        self.challenge_manager = get_daily_challenge_manager()
        self.modifier_applier = get_modifier_applier()
        self.modifier_applier.initialize(self.challenge_manager)
        
        self.is_challenge_mode = False
        self.challenge_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.challenge_mode_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20,
            200, 50, "每日挑战", YELLOW, (200, 180, 0)
        )
        
        self.challenge_pause_continue_button = Button(
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20,
            200, 50, "继续挑战", YELLOW, (200, 180, 0)
        )
    
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
        
        if self.is_challenge_mode:
            self._end_challenge_mode()
        
        self.render_surface.fill(BLACK)
        self.challenge_surface.fill(BLACK)
        
        self.ship = Ship()
        self.ship.speed = 7 + self.skill_tree.get_total_move_speed()
        
        self.meteors = []
        self.powerups = []
        self.bullets = []
        self.particle_system = ParticleSystem()
        self.text_manager = FloatingTextManager()
        self.score = 0
        
        base_lives = 3
        skill_lives = self.skill_tree.get_total_max_life()
        self.max_lives = base_lives + skill_lives
        self.lives = self.max_lives
        
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
        self.bullet_cooldown_frames = max(1, self.base_bullet_cooldown_frames - self.skill_tree.get_fire_rate_reduction())
        
        self.meteor_slow = False
        self.meteor_slow_duration = 0
        
        self.has_energy_shield = False
        self.has_ultimate_mode = False
        self.ultimate_duration = 0
        
        self.ultimate_transition_in = False
        self.ultimate_transition_out = False
        self.ultimate_transition_timer = 0
        self.ultimate_transition_max = 45
        
        self.visual_effect_phase = 0
        
        self.move_sound_cooldown = 0
        
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_angle = 0
        
        if self.screen_shake:
            self.screen_shake.stop_shake()
        
        if self.combo_system:
            self.combo_system = ComboSystem()
            combo_extra = self.skill_tree.get_combo_duration_extra()
            if combo_extra > 0:
                self.combo_system.combo_timeout = FPS * 2 + combo_extra
        
        if self.difficulty_system:
            self.difficulty_system = DifficultySystem()
        
        if HAS_POST_PROCESSING:
            self.post_processor = PostProcessor()
        
        self.prev_ship_position = None
        self.ship_speed = 0
        
        self.audio_manager.play_music("background")
    
    def start_challenge_mode(self):
        self.is_challenge_mode = True
        self.modifier_applier.start_challenge_mode()
        
        self.render_surface.fill(BLACK)
        self.challenge_surface.fill(BLACK)
        
        self.ship = Ship()
        self.ship.speed = 7 + self.skill_tree.get_total_move_speed()
        
        self.meteors = []
        self.powerups = []
        self.bullets = []
        self.particle_system = ParticleSystem()
        self.text_manager = FloatingTextManager()
        self.score = 0
        
        if self.modifier_applier.is_fragile_ship():
            self.max_lives = 1
            self.lives = 1
        else:
            base_lives = 3
            skill_lives = self.skill_tree.get_total_max_life()
            self.max_lives = base_lives + skill_lives
            self.lives = self.max_lives
        
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
        
        if self.modifier_applier.is_infinite_bullets():
            self.has_bullet = True
            self.bullet_duration = float('inf')
        else:
            self.has_bullet = False
            self.bullet_duration = 0
        
        self.bullet_cooldown = 0
        self.bullet_cooldown_frames = max(1, self.base_bullet_cooldown_frames - self.skill_tree.get_fire_rate_reduction())
        
        self.meteor_slow = False
        self.meteor_slow_duration = 0
        
        self.has_energy_shield = False
        self.has_ultimate_mode = False
        self.ultimate_duration = 0
        
        self.ultimate_transition_in = False
        self.ultimate_transition_out = False
        self.ultimate_transition_timer = 0
        self.ultimate_transition_max = 45
        
        self.visual_effect_phase = 0
        
        self.move_sound_cooldown = 0
        
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_angle = 0
        
        if self.screen_shake:
            self.screen_shake.stop_shake()
        
        if self.combo_system:
            self.combo_system = ComboSystem()
            combo_extra = self.skill_tree.get_combo_duration_extra()
            if combo_extra > 0:
                self.combo_system.combo_timeout = FPS * 2 + combo_extra
        
        if self.difficulty_system:
            self.difficulty_system = DifficultySystem()
        
        if HAS_POST_PROCESSING:
            self.post_processor = PostProcessor()
        
        self.prev_ship_position = None
        self.ship_speed = 0
        
        self.audio_manager.play_music("background")
    
    def _end_challenge_mode(self):
        if self.score > 0:
            record = self.challenge_manager.record_challenge_completion(self.score)
        
        self.is_challenge_mode = False
        self.modifier_applier.end_challenge_mode()
    
    def get_challenge_stars(self) -> int:
        return self.challenge_manager.calculate_stars(self.score)
    
    def add_score_with_combo(self, base_score, source=""):
        if self.combo_system:
            multiplier = self.combo_system.add_hit(1)
            final_score = int(base_score * multiplier)
            self.score += final_score
            
            if multiplier > 1.0:
                self.text_manager.add_score_text(SCREEN_WIDTH // 2, 100, final_score)
            else:
                self.text_manager.add_score_text(SCREEN_WIDTH // 2, 100, base_score)
        else:
            self.score += base_score
            self.text_manager.add_score_text(SCREEN_WIDTH // 2, 100, base_score)
    
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
            
            is_penetrating = False
            is_freezing = False
            penetration_count = 0
            size_multiplier = 1.0
            
            if self.has_shield and self.has_bullet:
                is_penetrating = True
                penetration_count = SYNERGY_CONFIG["penetrating"]["penetration_count"]
                size_multiplier = SYNERGY_CONFIG["penetrating"]["size_multiplier"]
            elif self.has_bullet and self.meteor_slow:
                is_freezing = True
            
            skill_penetration = self.skill_tree.get_penetration_count()
            if skill_penetration > 0 and not is_penetrating:
                is_penetrating = True
                penetration_count = skill_penetration
            elif skill_penetration > 0 and is_penetrating:
                penetration_count += skill_penetration
            
            self.bullets.append(Bullet(
                ship_center_x, 
                ship_top_y, 
                is_penetrating=is_penetrating,
                is_freezing=is_freezing,
                penetration_count=penetration_count,
                size_multiplier=size_multiplier
            ))
            self.bullet_cooldown = self.bullet_cooldown_frames
            
            if is_penetrating:
                self.audio_manager.play_sound(SoundType.PENETRATING_SHOOT)
            else:
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
    
    def create_explosion_chain(self, source_meteor, chain_level=0):
        explosion_center = source_meteor.get_center()
        base_radius = source_meteor.get_explosion_radius()
        explosion_range_multiplier = self.skill_tree.get_explosion_range_multiplier()
        explosion_radius = int(base_radius * explosion_range_multiplier)
        
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
                        split_score = meteor.get_split_score()
                        for split_meteor in split_meteors:
                            split_center = split_meteor.get_center()
                            self.particle_system.create_explosion(
                                split_center[0], split_center[1], 5
                            )
                            self.meteors.append(split_meteor)
                            self.add_score_with_combo(split_score, "split_destroy")
                    
                    if meteor.should_explode_on_destroy():
                        self.create_explosion_chain(meteor, chain_level + 1)
                    
                    score_value = meteor.config.get("score", 10)
                    self.add_score_with_combo(score_value, "explosion_destroy")
                    
                    if chain_level > 0 and source_meteor.is_explosive():
                        chain_bonus = source_meteor.get_chain_explosion_bonus()
                        self.add_score_with_combo(chain_bonus, "chain_explosion")
                    
                    self.meteors.remove(meteor)
    
    def check_bullet_collisions(self):
        for bullet in self.bullets[:]:
            for meteor in self.meteors[:]:
                if bullet.rect.colliderect(meteor.rect):
                    meteor_center = meteor.get_center()
                    
                    if bullet.is_freezing:
                        if random.random() < SYNERGY_CONFIG["freeze"]["freeze_chance"]:
                            meteor.freeze(SYNERGY_CONFIG["freeze"]["freeze_duration"])
                            self.audio_manager.play_sound(SoundType.FREEZE)
                    
                    meteor_size = max(meteor.width, meteor.height)
                    
                    if self.screen_shake:
                        self.screen_shake.add_trauma(0.15)
                    
                    if meteor.is_explosive():
                        meteor.activate_fuse()
                    
                    base_damage = 2 + self.skill_tree.get_total_bullet_damage()
                    if self.has_ultimate_mode:
                        base_damage *= SYNERGY_CONFIG["ultimate"]["bullet_damage_multiplier"]
                    bullet_damage = meteor.get_bullet_damage(base_damage)
                    
                    if meteor.take_damage(bullet_damage):
                        if meteor.should_explode_on_destroy():
                            self.create_explosion_chain(meteor)
                        else:
                            self.particle_system.create_layered_explosion(
                                meteor_center[0], meteor_center[1],
                                meteor_type=meteor.type,
                                meteor_size=meteor_size
                            )
                            
                            if self.screen_shake:
                                self.screen_shake.add_trauma(0.3)
                            
                            if meteor.can_split():
                                split_meteors = meteor.get_split_meteors()
                                split_score = meteor.get_split_score()
                                for split_meteor in split_meteors:
                                    split_center = split_meteor.get_center()
                                    self.particle_system.create_layered_explosion(
                                        split_center[0], split_center[1],
                                        meteor_type=split_meteor.type,
                                        meteor_size=max(split_meteor.width, split_meteor.height)
                                    )
                                    self.meteors.append(split_meteor)
                                    self.add_score_with_combo(split_score, "split_destroy")
                            
                            score_value = meteor.config.get("score", 10)
                            self.add_score_with_combo(score_value, "destroy")
                        
                        if meteor in self.meteors:
                            self.meteors.remove(meteor)
                        self.audio_manager.play_sound(SoundType.EXPLOSION)
                    else:
                        self.particle_system.create_explosion(
                            meteor_center[0], meteor_center[1], 8
                        )
                        self.audio_manager.play_sound(SoundType.HIT)
                    
                    if bullet.is_penetrating and bullet.can_penetrate():
                        bullet.use_penetration()
                        if not bullet.active:
                            self.bullets.remove(bullet)
                            break
                    else:
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
                    
                    if self.has_energy_shield or self.has_ultimate_mode:
                        shockwave_radius = SYNERGY_CONFIG["energy_shield"]["shockwave_radius"]
                        knockback_force = SYNERGY_CONFIG["energy_shield"]["knockback_force"]
                        
                        self.particle_system.create_knockback_shockwave(
                            ship_center[0], ship_center[1], shockwave_radius
                        )
                        
                        for other_meteor in self.meteors[:]:
                            if other_meteor is meteor:
                                continue
                            
                            other_center = other_meteor.get_center()
                            dx = ship_center[0] - other_center[0]
                            dy = ship_center[1] - other_center[1]
                            distance = math.sqrt(dx * dx + dy * dy)
                            
                            if distance <= shockwave_radius:
                                distance_ratio = 1.0 - (distance / shockwave_radius)
                                adjusted_force = knockback_force * (0.5 + 0.5 * distance_ratio)
                                other_meteor.apply_knockback(dx, dy, adjusted_force, distance_ratio)
                    
                    if meteor.take_damage():
                        if meteor.should_explode_on_destroy():
                            self.create_explosion_chain(meteor)
                        else:
                            self.particle_system.create_explosion(
                                meteor_center[0], meteor_center[1], 25
                            )
                            
                            if meteor.can_split():
                                split_meteors = meteor.get_split_meteors()
                                split_score = meteor.get_split_score()
                                for split_meteor in split_meteors:
                                    split_center = split_meteor.get_center()
                                    self.particle_system.create_explosion(
                                        split_center[0], split_center[1], 5
                                    )
                                    self.meteors.append(split_meteor)
                                    self.add_score_with_combo(split_score, "split_destroy")
                            
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
                    
                    collision_reduction = self.skill_tree.get_collision_damage_reduction()
                    damage_avoided = False
                    
                    if collision_reduction > 0:
                        if random.random() < collision_reduction:
                            damage_avoided = True
                    
                    if damage_avoided:
                        self.text_manager.add_text(
                            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                            "伤害减免！",
                            (100, 200, 255), duration=90, float_speed=0, font_size=36
                        )
                    else:
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
                
                powerup_duration_multiplier = self.skill_tree.get_powerup_duration_multiplier()
                shield_duration_extra = self.skill_tree.get_shield_duration_extra()
                
                if powerup.type == POWERUP_SHIELD:
                    self.has_shield = True
                    self.shield_duration = int(powerup.config["duration"] * powerup_duration_multiplier) + shield_duration_extra
                    self.shield_flash_timer = 0
                    self.show_shield_outline = True
                elif powerup.type == POWERUP_BULLET:
                    self.has_bullet = True
                    self.bullet_duration = int(powerup.config["duration"] * powerup_duration_multiplier)
                    self.bullet_cooldown = 0
                elif powerup.type == POWERUP_SLOW:
                    self.meteor_slow = True
                    self.meteor_slow_duration = int(powerup.config["duration"] * powerup_duration_multiplier)
                
                if self.has_shield and self.meteor_slow and not (self.has_shield and self.has_bullet):
                    self.has_energy_shield = True
                    self.shield_duration += SYNERGY_CONFIG["energy_shield"]["duration_extension"]
                    self.shield_color = SYNERGY_CONFIG["energy_shield"]["color"]
                    self.audio_manager.play_sound(SoundType.ENERGY_SHIELD)
                
                if self.has_shield and self.has_bullet and self.meteor_slow:
                    if not self.has_ultimate_mode:
                        self.has_ultimate_mode = True
                        self.ultimate_duration = SYNERGY_CONFIG["ultimate"]["duration"]
                        self.shield_color = SYNERGY_CONFIG["ultimate"]["color"]
                        self.ultimate_transition_in = True
                        self.ultimate_transition_timer = 0
                        self.audio_manager.play_sound(SoundType.ULTIMATE_ACTIVATE)
                
                display_text = powerup.config["name"]
                display_color = powerup.config["color"]
                
                if self.has_ultimate_mode:
                    display_text = SYNERGY_CONFIG["ultimate"]["name"]
                    display_color = SYNERGY_CONFIG["ultimate"]["color"]
                elif self.has_energy_shield:
                    display_text = SYNERGY_CONFIG["energy_shield"]["name"]
                    display_color = SYNERGY_CONFIG["energy_shield"]["color"]
                elif self.has_shield and self.has_bullet:
                    display_text = SYNERGY_CONFIG["penetrating"]["name"]
                    display_color = SYNERGY_CONFIG["penetrating"]["color"]
                elif self.has_bullet and self.meteor_slow:
                    display_text = SYNERGY_CONFIG["freeze"]["name"]
                    display_color = SYNERGY_CONFIG["freeze"]["color"]
                
                self.text_manager.add_text(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                    display_text,
                    display_color, duration=120, float_speed=0, font_size=48
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
                self.skill_tree.add_skill_points(1)
                
                if self.post_processor:
                    self.post_processor.trigger_upgrade()
                
                ship_center = (self.ship.x + self.ship.width // 2, self.ship.y + self.ship.height // 2)
                self.particle_system.create_upgrade_flash_particles(ship_center[0], ship_center[1])
        
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
            if not self.has_ultimate_mode:
                self.shield_duration -= 1
            self.shield_flash_timer += 1
            if self.shield_flash_timer >= self.shield_flash_interval:
                self.show_shield_outline = not self.show_shield_outline
                self.shield_flash_timer = 0
            if self.shield_duration <= 0 and not self.has_ultimate_mode:
                self.has_shield = False
                self.show_shield_outline = True
                self.has_energy_shield = False
                self.shield_color = SHIELD_BLUE
        
        if self.has_ultimate_mode:
            self.ultimate_duration -= 1
            self.visual_effect_phase += 1
            
            if self.ultimate_transition_in:
                self.ultimate_transition_timer += 1
                if self.ultimate_transition_timer >= self.ultimate_transition_max:
                    self.ultimate_transition_in = False
                    self.ultimate_transition_timer = 0
            
            if self.ultimate_duration <= 0 and not self.ultimate_transition_out:
                self.ultimate_transition_out = True
                self.ultimate_transition_timer = 0
            
            if self.ultimate_transition_out:
                self.ultimate_transition_timer += 1
                if self.ultimate_transition_timer >= self.ultimate_transition_max:
                    self.has_ultimate_mode = False
                    self.has_shield = False
                    self.has_bullet = False
                    self.meteor_slow = False
                    self.has_energy_shield = False
                    self.shield_color = SHIELD_BLUE
                    self.ultimate_transition_out = False
                    self.ultimate_transition_timer = 0
        else:
            self.visual_effect_phase += 1
        
        if self.has_bullet:
            if not self.has_ultimate_mode and not (self.is_challenge_mode and self.modifier_applier.is_infinite_bullets()):
                self.bullet_duration -= 1
                if self.bullet_duration <= 0:
                    self.has_bullet = False
                    self.bullet_cooldown = 0
            if self.bullet_cooldown > 0:
                self.bullet_cooldown -= 1
        
        if self.meteor_slow and not self.has_ultimate_mode:
            self.meteor_slow_duration -= 1
            if self.meteor_slow_duration <= 0:
                self.meteor_slow = False
                self.has_energy_shield = False
                self.shield_color = SHIELD_BLUE
        
        if self.has_energy_shield and self.visual_effect_phase % 8 == 0:
            ship_center = (self.ship.x + self.ship.width // 2, 
                           self.ship.y + self.ship.height // 2)
            shield_radius = max(self.ship.width, self.ship.height) // 2 + 15
            self.particle_system.create_energy_wave_particles(
                ship_center[0], ship_center[1], shield_radius, self.visual_effect_phase
            )
        
        if self.has_ultimate_mode and self.visual_effect_phase % 6 == 0:
            ship_center = (self.ship.x + self.ship.width // 2, 
                           self.ship.y + self.ship.height // 2)
            self.particle_system.create_ship_glow_particles(
                ship_center[0], ship_center[1], self.visual_effect_phase
            )
        
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
                continue
            
            combo_count = self.combo_system.get_combo() if self.combo_system else 0
            is_high_combo = combo_count >= HIGH_COMBO_THRESHOLD
            
            trail_x, trail_y = bullet.get_trail_position()
            self.particle_system.create_bullet_trail(
                trail_x, trail_y,
                is_high_combo=is_high_combo,
                is_penetrating=bullet.is_penetrating
            )
        
        for meteor in self.meteors[:]:
            if meteor.is_frozen:
                meteor.update()
                if meteor.y > SCREEN_HEIGHT:
                    meteor_center = meteor.get_center()
                    self.particle_system.create_explosion(meteor_center[0], SCREEN_HEIGHT - 20, 12)
                    self.meteors.remove(meteor)
                    
                    score_value = meteor.config.get("score", 10)
                    dodge_multiplier = self.skill_tree.get_dodge_reward_multiplier()
                    final_score = int(score_value * dodge_multiplier)
                    self.add_score_with_combo(final_score, "dodge")
                    self.audio_manager.play_sound(SoundType.DODGE)
                continue
            
            speed_multiplier = 1.0
            if self.difficulty_system:
                speed_multiplier = self.difficulty_system.get_meteor_speed_multiplier()
            
            if self.is_challenge_mode:
                time_multiplier = self.modifier_applier.get_time_multiplier()
                speed_multiplier *= time_multiplier
                
                if self.modifier_applier.is_gravity_reversed():
                    if self.has_ultimate_mode:
                        meteor.y -= meteor.speed * SYNERGY_CONFIG["ultimate"]["meteor_speed_multiplier"] * speed_multiplier
                        meteor.rect.y = meteor.y
                    elif self.meteor_slow and meteor.speed > 2:
                        meteor.y -= meteor.speed * 0.5 * speed_multiplier
                        meteor.rect.y = meteor.y
                    else:
                        meteor.y -= meteor.speed * speed_multiplier
                        meteor.rect.y = meteor.y
                        meteor.update()
                else:
                    if self.has_ultimate_mode:
                        meteor.y += meteor.speed * SYNERGY_CONFIG["ultimate"]["meteor_speed_multiplier"] * speed_multiplier
                        meteor.rect.y = meteor.y
                    elif self.meteor_slow and meteor.speed > 2:
                        meteor.y += meteor.speed * 0.5 * speed_multiplier
                        meteor.rect.y = meteor.y
                    else:
                        meteor.y += meteor.speed * speed_multiplier
                        meteor.rect.y = meteor.y
                        meteor.update()
            else:
                if self.has_ultimate_mode:
                    meteor.y += meteor.speed * SYNERGY_CONFIG["ultimate"]["meteor_speed_multiplier"] * speed_multiplier
                    meteor.rect.y = meteor.y
                elif self.meteor_slow and meteor.speed > 2:
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
            
            if self.is_challenge_mode and self.modifier_applier.is_gravity_reversed():
                if meteor.y + meteor.height < 0:
                    meteor_center = meteor.get_center()
                    self.particle_system.create_explosion(meteor_center[0], 20, 12)
                    self.meteors.remove(meteor)
                    
                    score_value = meteor.config.get("score", 10)
                    dodge_multiplier = self.skill_tree.get_dodge_reward_multiplier()
                    final_score = int(score_value * dodge_multiplier)
                    self.add_score_with_combo(final_score, "dodge")
                    self.audio_manager.play_sound(SoundType.DODGE)
            else:
                if meteor.y > SCREEN_HEIGHT:
                    meteor_center = meteor.get_center()
                    self.particle_system.create_explosion(meteor_center[0], SCREEN_HEIGHT - 20, 12)
                    self.meteors.remove(meteor)
                    
                    score_value = meteor.config.get("score", 10)
                    dodge_multiplier = self.skill_tree.get_dodge_reward_multiplier()
                    final_score = int(score_value * dodge_multiplier)
                    self.add_score_with_combo(final_score, "dodge")
                    self.audio_manager.play_sound(SoundType.DODGE)
        
        for powerup in self.powerups[:]:
            if not powerup.update():
                self.powerups.remove(powerup)
        
        self.check_bullet_collisions()
        self.check_collisions()
        self.check_powerup_collisions()
        self.particle_system.update()
        self.text_manager.update()
        
        if self.post_processor:
            ship_center = (self.ship.x + self.ship.width // 2, self.ship.y + self.ship.height // 2)
            
            if self.prev_ship_position is not None:
                dx = ship_center[0] - self.prev_ship_position[0]
                dy = ship_center[1] - self.prev_ship_position[1]
                self.ship_speed = math.sqrt(dx * dx + dy * dy)
            else:
                self.ship_speed = 0
            
            self.prev_ship_position = ship_center
            
            combo_count = self.combo_system.get_combo() if self.combo_system else 0
            self.post_processor.update(
                ship_position=ship_center,
                ship_speed=self.ship_speed,
                combo_count=combo_count,
                current_lives=self.lives
            )
        
        if self.lives <= 1 and self.post_processor:
            ship_center = (self.ship.x + self.ship.width // 2, self.ship.y + self.ship.height // 2)
            if random.random() < 0.1:
                self.particle_system.create_danger_particles(ship_center[0], ship_center[1])
        
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
    
    def _draw_text_with_shadow(self, surface, text, font, pos, color, shadow_color=(0, 0, 0), shadow_offset=2):
        shadow_text = font.render(text, True, shadow_color)
        shadow_rect = shadow_text.get_rect(center=pos)
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        surface.blit(shadow_text, shadow_rect)
        
        main_text = font.render(text, True, color)
        main_rect = main_text.get_rect(center=pos)
        surface.blit(main_text, main_rect)
    
    def draw_powerup_status(self, surface):
        status_x = SCREEN_WIDTH - 15
        status_y = 80
        status_spacing = 28
        
        active_powerups = []
        synergy_active = False
        synergy_name = ""
        synergy_color = (255, 255, 255)
        synergy_icon = ""
        
        if self.has_ultimate_mode:
            synergy_active = True
            synergy_name = "终极模式"
            synergy_color = SYNERGY_CONFIG["ultimate"]["color"]
            synergy_icon = "👑"
        elif self.has_energy_shield:
            synergy_active = True
            synergy_name = "能量护盾"
            synergy_color = SYNERGY_CONFIG["energy_shield"]["color"]
            synergy_icon = "🔮"
        elif self.has_shield and self.has_bullet:
            synergy_active = True
            synergy_name = "穿透护盾"
            synergy_color = SYNERGY_CONFIG["penetrating"]["color"]
            synergy_icon = "🌟"
        elif self.has_bullet and self.meteor_slow:
            synergy_active = True
            synergy_name = "冰冻子弹"
            synergy_color = SYNERGY_CONFIG["freeze"]["color"]
            synergy_icon = "❄️"
        
        if not self.has_ultimate_mode:
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
        
        small_font = get_small_font()
        
        for i, powerup in enumerate(active_powerups):
            current_y = status_y + i * status_spacing
            
            icon_text = small_font.render(powerup["icon"], True, powerup["color"])
            icon_rect = icon_text.get_rect(midright=(status_x - 35, current_y))
            surface.blit(icon_text, icon_rect)
            
            is_infinite = powerup["duration"] == float('inf')
            if is_infinite:
                time_str = "∞"
            else:
                seconds_remaining = max(0, (powerup["duration"] + FPS - 1) // FPS)
                time_str = f"{seconds_remaining}s"
            
            self._draw_text_with_shadow(
                surface, time_str, small_font,
                (status_x, current_y), powerup["color"]
            )
        
        if synergy_active:
            synergy_y = status_y + len(active_powerups) * status_spacing + 12
            
            icon_text = small_font.render(synergy_icon, True, synergy_color)
            icon_rect = icon_text.get_rect(midright=(status_x - 35, synergy_y))
            surface.blit(icon_text, icon_rect)
            
            if self.has_ultimate_mode:
                seconds_remaining = max(0, (self.ultimate_duration + FPS - 1) // FPS)
                time_str = f"{seconds_remaining}s"
                self._draw_text_with_shadow(
                    surface, time_str, small_font,
                    (status_x, synergy_y), synergy_color
                )
            else:
                self._draw_text_with_shadow(
                    surface, synergy_name, small_font,
                    (status_x - 10, synergy_y), synergy_color
                )
    
    def draw_ship_with_shield(self, surface):
        self.ship.draw(surface)
        
        if self.has_shield and self.show_shield_outline:
            ship_center_x = self.ship.x + self.ship.width // 2
            ship_center_y = self.ship.y + self.ship.height // 2
            
            base_shield_radius = max(self.ship.width, self.ship.height) // 2 + 15
            
            pulse_time = self.visual_effect_phase * 0.05
            pulse_intensity = 0.8 + 0.2 * math.sin(pulse_time * 3)
            pulse_offset = 3 * math.sin(pulse_time * 2)
            
            shield_radius = int(base_shield_radius * pulse_intensity + pulse_offset)
            
            shield_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            
            if self.has_ultimate_mode:
                self._draw_ultimate_shield(shield_surface, ship_center_x, ship_center_y, shield_radius, pulse_time)
            elif self.has_energy_shield:
                self._draw_energy_shield(shield_surface, ship_center_x, ship_center_y, shield_radius, pulse_time)
            else:
                self._draw_normal_shield(shield_surface, ship_center_x, ship_center_y, shield_radius, pulse_time)
            
            surface.blit(shield_surface, (0, 0))
    
    def _draw_normal_shield(self, surface, cx, cy, radius, pulse_time):
        outer_alpha = int(120 + 40 * math.sin(pulse_time * 2.5))
        inner_alpha = int(180 + 40 * math.sin(pulse_time * 2.5))
        
        pygame.draw.circle(
            surface,
            (*self.shield_color, outer_alpha),
            (cx, cy),
            radius + 5,
            2
        )
        
        pygame.draw.circle(
            surface,
            (*self.shield_color, inner_alpha),
            (cx, cy),
            radius,
            3
        )
        
        pygame.draw.polygon(
            surface, 
            (*self.shield_color, 100),
            [
                (cx, self.ship.y - 8),
                (self.ship.x - 8, self.ship.y + self.ship.height + 8),
                (self.ship.x + self.ship.width + 8, self.ship.y + self.ship.height + 8)
            ],
            2
        )
    
    def _draw_energy_shield(self, surface, cx, cy, radius, pulse_time):
        outer_radius = radius + 8
        inner_radius = radius - 2
        
        for layer in range(3):
            layer_radius = outer_radius - layer * 5
            layer_alpha = int(60 + 40 * math.sin(pulse_time * 2.5 + layer * 1.5))
            layer_thickness = 3 if layer == 1 else 2
            
            if layer == 0:
                layer_color = ENERGY_SHIELD_LIGHT_PURPLE
            else:
                layer_color = ENERGY_SHIELD_PURPLE
            
            pygame.draw.circle(
                surface,
                (*layer_color, layer_alpha),
                (cx, cy),
                layer_radius,
                layer_thickness
            )
        
        num_energy_points = 8
        for i in range(num_energy_points):
            angle = (i / num_energy_points) * math.pi * 2 + pulse_time * 1.5
            point_radius = inner_radius + 5 * math.sin(pulse_time * 3 + i)
            px = cx + math.cos(angle) * point_radius
            py = cy + math.sin(angle) * point_radius
            
            point_alpha = int(150 + 80 * math.sin(pulse_time * 4 + i))
            point_size = 3 + 2 * math.sin(pulse_time * 2 + i * 0.5)
            
            pygame.draw.circle(
                surface,
                (*ENERGY_SHIELD_LIGHT_PURPLE, point_alpha),
                (int(px), int(py)),
                int(point_size)
            )
        
        center_alpha = int(80 + 50 * math.sin(pulse_time * 3))
        pygame.draw.circle(
            surface,
            (*ENERGY_SHIELD_PURPLE, center_alpha),
            (cx, cy),
            15,
            0
        )
        
        pygame.draw.circle(
            surface,
            (*ENERGY_SHIELD_LIGHT_PURPLE, int(100 + 50 * math.sin(pulse_time * 2))),
            (cx, cy),
            10,
            0
        )
    
    def _draw_ultimate_shield(self, surface, cx, cy, radius, pulse_time):
        outer_radius = radius + 12
        middle_radius = radius + 5
        inner_radius = radius - 3
        
        for i in range(3):
            angle = pulse_time * 2 + i * (math.pi * 2 / 3)
            spiral_radius = outer_radius + 10 * math.sin(pulse_time + i)
            
            for j in range(3):
                spiral_angle = angle + j * 0.3
                spiral_px = cx + math.cos(spiral_angle) * (spiral_radius - j * 8)
                spiral_py = cy + math.sin(spiral_angle) * (spiral_radius - j * 8)
                
                spiral_alpha = int(80 + 60 * math.sin(pulse_time * 3 + i + j))
                pygame.draw.circle(
                    surface,
                    (*ULTIMATE_LIGHT_GOLD, spiral_alpha),
                    (int(spiral_px), int(spiral_py)),
                    4 - j
                )
        
        pygame.draw.circle(
            surface,
            (*ULTIMATE_GOLD, int(100 + 60 * math.sin(pulse_time * 2.5))),
            (cx, cy),
            outer_radius,
            3
        )
        
        pygame.draw.circle(
            surface,
            (*ULTIMATE_LIGHT_GOLD, int(150 + 80 * math.sin(pulse_time * 3))),
            (cx, cy),
            middle_radius,
            2
        )
        
        pygame.draw.circle(
            surface,
            (*ULTIMATE_GOLD, int(200 + 50 * math.sin(pulse_time * 2))),
            (cx, cy),
            inner_radius,
            0
        )
        
        num_light_points = 12
        for i in range(num_light_points):
            angle = (i / num_light_points) * math.pi * 2 + pulse_time * 2
            light_radius = middle_radius + 8 * math.sin(pulse_time * 2.5 + i)
            lx = cx + math.cos(angle) * light_radius
            ly = cy + math.sin(angle) * light_radius
            
            light_alpha = int(100 + 100 * math.sin(pulse_time * 4 + i * 0.8))
            light_size = 2 + 3 * math.sin(pulse_time * 3 + i)
            
            pygame.draw.circle(
                surface,
                (*ULTIMATE_LIGHT_GOLD, light_alpha),
                (int(lx), int(ly)),
                max(1, int(light_size))
            )
        
        for i in range(3):
            ring_radius = 20 + i * 8
            ring_alpha = int(120 + 80 * math.sin(pulse_time * 3 + i * 1.2))
            ring_thickness = 2 if i == 1 else 1
            
            pygame.draw.circle(
                surface,
                (*ULTIMATE_GOLD, ring_alpha),
                (cx, cy),
                ring_radius,
                ring_thickness
            )
    
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
                
                warning_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(warning_overlay, border_color, (0, 0, SCREEN_WIDTH, border_thickness))
                pygame.draw.rect(warning_overlay, border_color, (0, SCREEN_HEIGHT - border_thickness, SCREEN_WIDTH, border_thickness))
                pygame.draw.rect(warning_overlay, border_color, (0, 0, border_thickness, SCREEN_HEIGHT))
                pygame.draw.rect(warning_overlay, border_color, (SCREEN_WIDTH - border_thickness, 0, border_thickness, SCREEN_HEIGHT))
                surface.blit(warning_overlay, (0, 0))
        
        if self.has_ultimate_mode:
            seconds_remaining = max(0, (self.ultimate_duration + FPS - 1) // FPS)
            
            if seconds_remaining <= 2 and seconds_remaining > 0:
                self._draw_ultimate_countdown_warning(surface, seconds_remaining)
        
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
    
    def _draw_ultimate_countdown_warning(self, surface, seconds_remaining):
        warning_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        flash_speed = 8 if seconds_remaining == 1 else 12
        flash_frame = self.visual_effect_phase // flash_speed
        should_flash = flash_frame % 2 == 0
        
        if should_flash:
            border_thickness = 25
            
            if seconds_remaining == 1:
                border_color = (255, 80, 0, 180)
            else:
                border_color = (255, 150, 0, 120)
            
            pygame.draw.rect(warning_surface, border_color, (0, 0, SCREEN_WIDTH, border_thickness))
            pygame.draw.rect(warning_surface, border_color, (0, SCREEN_HEIGHT - border_thickness, SCREEN_WIDTH, border_thickness))
            pygame.draw.rect(warning_surface, border_color, (0, 0, border_thickness, SCREEN_HEIGHT))
            pygame.draw.rect(warning_surface, border_color, (SCREEN_WIDTH - border_thickness, 0, border_thickness, SCREEN_HEIGHT))
            
            corner_size = 80
            corner_alpha = int(border_color[3] * 1.3)
            corner_color = (border_color[0], border_color[1], border_color[2], min(255, corner_alpha))
            
            pygame.draw.rect(warning_surface, corner_color, (0, 0, corner_size, border_thickness))
            pygame.draw.rect(warning_surface, corner_color, (0, 0, border_thickness, corner_size))
            pygame.draw.rect(warning_surface, corner_color, (SCREEN_WIDTH - corner_size, 0, corner_size, border_thickness))
            pygame.draw.rect(warning_surface, corner_color, (SCREEN_WIDTH - border_thickness, 0, border_thickness, corner_size))
            pygame.draw.rect(warning_surface, corner_color, (0, SCREEN_HEIGHT - border_thickness, corner_size, border_thickness))
            pygame.draw.rect(warning_surface, corner_color, (0, SCREEN_HEIGHT - corner_size, border_thickness, corner_size))
            pygame.draw.rect(warning_surface, corner_color, (SCREEN_WIDTH - corner_size, SCREEN_HEIGHT - border_thickness, corner_size, border_thickness))
            pygame.draw.rect(warning_surface, corner_color, (SCREEN_WIDTH - border_thickness, SCREEN_HEIGHT - corner_size, border_thickness, corner_size))
        
        from game.core.utils import get_large_font, get_font
        text_scale = 1.2 + 0.3 * math.sin(self.visual_effect_phase * 0.2)
        
        countdown_text = get_large_font().render(f"{seconds_remaining}", True, (255, 200, 0))
        scaled_size = int(countdown_text.get_width() * text_scale), int(countdown_text.get_height() * text_scale)
        countdown_scaled = pygame.transform.scale(countdown_text, scaled_size)
        countdown_rect = countdown_scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        
        if should_flash:
            surface.blit(warning_surface, (0, 0))
        
        surface.blit(countdown_scaled, countdown_rect)
        
        hint_text = get_font().render("终极模式即将结束!", True, (255, 220, 100))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(hint_text, hint_rect)
    
    def draw_difficulty_level_up(self, surface):
        if self.difficulty_system and self.difficulty_system.should_display_level_up():
            self.difficulty_system.draw_level_up(surface, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    def draw_ultimate_golden_halo(self, surface):
        if not self.has_ultimate_mode:
            return
        
        pulse_time = self.visual_effect_phase * 0.05
        base_alpha = int(70 + 50 * math.sin(pulse_time * 1.5))
        max_border_thickness = 35
        
        halo_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        self._draw_gradient_border(halo_surface, max_border_thickness, base_alpha, pulse_time)
        
        self._draw_corner_decorations(halo_surface, base_alpha, pulse_time)
        
        self._draw_flowing_light_points(halo_surface, pulse_time)
        
        surface.blit(halo_surface, (0, 0))
    
    def _draw_gradient_border(self, surface, max_thickness, base_alpha, pulse_time):
        for layer in range(5):
            layer_thickness = max_thickness - layer * 6
            layer_alpha = max(0, min(255, int(base_alpha * (0.3 + 0.15 * layer))))
            
            pulse_offset = int(2 * math.sin(pulse_time * 2 + layer * 0.8))
            actual_thickness = max(1, layer_thickness + pulse_offset)
            
            r = min(255, int(ULTIMATE_GOLD[0] * (0.8 + 0.04 * layer)))
            g = min(255, int(ULTIMATE_GOLD[1] * (0.85 + 0.03 * layer)))
            b = min(255, int(ULTIMATE_GOLD[2] * (0.7 + 0.06 * layer)))
            
            border_color = (r, g, b, layer_alpha)
            
            pygame.draw.rect(
                surface,
                border_color,
                (0, 0, SCREEN_WIDTH, actual_thickness)
            )
            pygame.draw.rect(
                surface,
                border_color,
                (0, SCREEN_HEIGHT - actual_thickness, SCREEN_WIDTH, actual_thickness)
            )
            pygame.draw.rect(
                surface,
                border_color,
                (0, 0, actual_thickness, SCREEN_HEIGHT)
            )
            pygame.draw.rect(
                surface,
                border_color,
                (SCREEN_WIDTH - actual_thickness, 0, actual_thickness, SCREEN_HEIGHT)
            )
    
    def _draw_corner_decorations(self, surface, base_alpha, pulse_time):
        corner_size = 50
        inner_corner_size = 35
        
        corners = [
            (0, 0),
            (SCREEN_WIDTH, 0),
            (0, SCREEN_HEIGHT),
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        ]
        
        for corner_idx, (cx, cy) in enumerate(corners):
            angle_offset = corner_idx * math.pi * 0.5 + pulse_time * 0.5
            
            for ring in range(3):
                ring_radius = corner_size - ring * 12
                ring_alpha_unclamped = int(base_alpha * (0.5 + 0.25 * ring) * (1.2 + 0.3 * math.sin(pulse_time * 2 + corner_idx + ring)))
                ring_alpha = max(0, min(255, ring_alpha_unclamped))
                
                for dot_angle in range(0, 90, 15):
                    rad = math.radians(dot_angle) + angle_offset
                    dot_radius = ring_radius + 3 * math.sin(pulse_time * 3 + dot_angle * 0.1 + corner_idx)
                    
                    if corner_idx == 0:
                        dx = math.cos(rad) * dot_radius
                        dy = math.sin(rad) * dot_radius
                    elif corner_idx == 1:
                        dx = -math.cos(rad) * dot_radius
                        dy = math.sin(rad) * dot_radius
                    elif corner_idx == 2:
                        dx = math.cos(rad) * dot_radius
                        dy = -math.sin(rad) * dot_radius
                    else:
                        dx = -math.cos(rad) * dot_radius
                        dy = -math.sin(rad) * dot_radius
                    
                    dot_x = int(cx + dx)
                    dot_y = int(cy + dy)
                    dot_size = max(1, int(2 + ring * 0.5 + math.sin(pulse_time * 4 + dot_angle) * 1))
                    
                    dot_color = (
                        ULTIMATE_LIGHT_GOLD[0] if ring % 2 == 0 else ULTIMATE_GOLD[0],
                        ULTIMATE_LIGHT_GOLD[1] if ring % 2 == 0 else ULTIMATE_GOLD[1],
                        ULTIMATE_LIGHT_GOLD[2] if ring % 2 == 0 else ULTIMATE_GOLD[2],
                        ring_alpha
                    )
                    
                    pygame.draw.circle(surface, dot_color, (dot_x, dot_y), dot_size)
            
            decor_alpha = int(base_alpha * 1.5 * (1.1 + 0.3 * math.sin(pulse_time * 2.5 + corner_idx)))
            decor_color = (*ULTIMATE_GOLD, min(255, decor_alpha))
            
            if corner_idx == 0:
                pygame.draw.rect(surface, decor_color, (0, 0, corner_size, 8))
                pygame.draw.rect(surface, decor_color, (0, 0, 8, corner_size))
            elif corner_idx == 1:
                pygame.draw.rect(surface, decor_color, (SCREEN_WIDTH - corner_size, 0, corner_size, 8))
                pygame.draw.rect(surface, decor_color, (SCREEN_WIDTH - 8, 0, 8, corner_size))
            elif corner_idx == 2:
                pygame.draw.rect(surface, decor_color, (0, SCREEN_HEIGHT - 8, corner_size, 8))
                pygame.draw.rect(surface, decor_color, (0, SCREEN_HEIGHT - corner_size, 8, corner_size))
            else:
                pygame.draw.rect(surface, decor_color, (SCREEN_WIDTH - corner_size, SCREEN_HEIGHT - 8, corner_size, 8))
                pygame.draw.rect(surface, decor_color, (SCREEN_WIDTH - 8, SCREEN_HEIGHT - corner_size, 8, corner_size))
    
    def _draw_flowing_light_points(self, surface, pulse_time):
        num_points_per_side = 6
        
        for side in range(4):
            for i in range(num_points_per_side):
                progress = (i / num_points_per_side + pulse_time * 0.8 + side * 0.1) % 1.0
                
                point_alpha = int(80 + 70 * math.sin(progress * math.pi))
                point_size = int(2 + 2 * math.sin(progress * math.pi))
                
                if point_alpha <= 0:
                    continue
                
                if side == 0:
                    x = int(progress * SCREEN_WIDTH)
                    y = 20 + int(5 * math.sin(pulse_time * 3 + i))
                elif side == 1:
                    x = int(SCREEN_WIDTH - 20 - 5 * math.sin(pulse_time * 3 + i))
                    y = int(progress * SCREEN_HEIGHT)
                elif side == 2:
                    x = int((1 - progress) * SCREEN_WIDTH)
                    y = int(SCREEN_HEIGHT - 20 - 5 * math.sin(pulse_time * 3 + i))
                else:
                    x = int(20 + 5 * math.sin(pulse_time * 3 + i))
                    y = int((1 - progress) * SCREEN_HEIGHT)
                
                point_color = (
                    ULTIMATE_LIGHT_GOLD[0] if i % 2 == 0 else ULTIMATE_GOLD[0],
                    ULTIMATE_LIGHT_GOLD[1] if i % 2 == 0 else ULTIMATE_GOLD[1],
                    ULTIMATE_LIGHT_GOLD[2] if i % 2 == 0 else ULTIMATE_GOLD[2],
                    point_alpha
                )
                
                pygame.draw.circle(surface, point_color, (x, y), max(1, point_size))
                
                if point_size >= 2:
                    trail_alpha = int(point_alpha * 0.5)
                    trail_color = (
                        point_color[0],
                        point_color[1],
                        point_color[2],
                        trail_alpha
                    )
                    pygame.draw.circle(surface, trail_color, (x, y), point_size + 1)
    
    def draw_ultimate_transition_effects(self, surface):
        if self.ultimate_transition_in:
            self._draw_ultimate_activate_transition(surface)
        
        if self.ultimate_transition_out:
            self._draw_ultimate_deactivate_transition(surface)
    
    def _draw_ultimate_activate_transition(self, surface):
        progress = self.ultimate_transition_timer / self.ultimate_transition_max
        
        if progress >= 1.0:
            return
        
        transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        flash_alpha = int(255 * (1.0 - progress) * 0.6)
        if flash_alpha > 0:
            transition_surface.fill((255, 248, 220, flash_alpha))
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        max_radius = max(SCREEN_WIDTH, SCREEN_HEIGHT) // 1.5
        
        for ring in range(3):
            ring_progress = progress - ring * 0.1
            if ring_progress < 0:
                continue
            
            ring_radius = int(max_radius * ring_progress)
            ring_alpha = int(200 * (1.0 - ring_progress) * (0.7 + ring * 0.15))
            
            if ring_radius > 0 and ring_alpha > 0:
                if ring == 0:
                    ring_color = (*ULTIMATE_GOLD, ring_alpha)
                elif ring == 1:
                    ring_color = (*ULTIMATE_LIGHT_GOLD, ring_alpha)
                else:
                    ring_color = (255, 255, 200, ring_alpha)
                
                pygame.draw.circle(
                    transition_surface,
                    ring_color,
                    (center_x, center_y),
                    ring_radius,
                    max(1, int(8 - ring * 2))
                )
        
        particle_count = int(12 * progress)
        for i in range(particle_count):
            angle = (i / 12) * math.pi * 2 + progress * 3
            dist = max_radius * progress * 0.8
            px = center_x + math.cos(angle) * dist
            py = center_y + math.sin(angle) * dist
            
            particle_alpha = int(180 * (1.0 - progress))
            particle_size = int(3 + 2 * math.sin(progress * math.pi * 2 + i))
            
            if particle_alpha > 0:
                pygame.draw.circle(
                    transition_surface,
                    (*ULTIMATE_LIGHT_GOLD, particle_alpha),
                    (int(px), int(py)),
                    particle_size
                )
        
        surface.blit(transition_surface, (0, 0))
    
    def _draw_ultimate_deactivate_transition(self, surface):
        progress = self.ultimate_transition_timer / self.ultimate_transition_max
        
        if progress >= 1.0:
            return
        
        transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        fade_alpha = int(150 * progress * 0.4)
        if fade_alpha > 0:
            transition_surface.fill((0, 0, 50, fade_alpha))
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        max_radius = max(SCREEN_WIDTH, SCREEN_HEIGHT) // 1.2
        
        for ring in range(3):
            ring_progress = 1.0 - progress - ring * 0.1
            if ring_progress < 0:
                continue
            
            ring_radius = int(max_radius * ring_progress)
            ring_alpha = int(180 * ring_progress * (0.7 + ring * 0.15))
            
            if ring_radius > 0 and ring_alpha > 0:
                if ring == 0:
                    ring_color = (*ULTIMATE_GOLD, ring_alpha)
                elif ring == 1:
                    ring_color = (*ULTIMATE_LIGHT_GOLD, ring_alpha)
                else:
                    ring_color = (255, 255, 200, ring_alpha)
                
                pygame.draw.circle(
                    transition_surface,
                    ring_color,
                    (center_x, center_y),
                    ring_radius,
                    max(1, int(6 - ring * 1.5))
                )
        
        particle_count = int(8 * (1.0 - progress))
        for i in range(particle_count):
            angle = (i / 8) * math.pi * 2 - progress * 2
            dist = max_radius * (1.0 - progress) * 0.7
            px = center_x + math.cos(angle) * dist
            py = center_y + math.sin(angle) * dist
            
            particle_alpha = int(150 * (1.0 - progress))
            particle_size = int(2 + 1.5 * math.sin((1.0 - progress) * math.pi + i))
            
            if particle_alpha > 0:
                pygame.draw.circle(
                    transition_surface,
                    (*ULTIMATE_LIGHT_GOLD, particle_alpha),
                    (int(px), int(py)),
                    particle_size
                )
        
        surface.blit(transition_surface, (0, 0))
    
    def draw(self, surface, mouse_pos):
        needs_mirror = self.is_challenge_mode and self.modifier_applier.is_mirror_mode()
        needs_shake = self.shake_offset_x != 0 or self.shake_offset_y != 0 or self.shake_angle != 0
        
        combo_count = self.combo_system.get_combo() if self.combo_system else 0
        is_high_combo = combo_count >= HIGH_COMBO_THRESHOLD
        
        if not self.game_started:
            if self.starfield:
                self.starfield.draw(surface)
            self.draw_start_screen(surface, mouse_pos)
            return
        
        if self.game_over:
            if self.starfield:
                self.starfield.draw(surface)
            self.draw_game_over_screen(surface, mouse_pos)
            return
        
        game_surface = self.render_surface
        game_surface.fill(BLACK)
        
        if self.starfield:
            self.starfield.draw(game_surface)
        
        self.particle_system.draw(game_surface)
        
        if not (self.collision_happened and self.collision_delay > 0):
            for powerup in self.powerups:
                powerup.draw(game_surface)
            
            for meteor in self.meteors:
                meteor.draw(game_surface)
            
            for bullet in self.bullets:
                bullet.draw_with_combo_effect(game_surface, is_high_combo=is_high_combo, combo_count=combo_count)
            
            if self.has_shield:
                self.draw_ship_with_shield(game_surface)
            else:
                self.ship.draw(game_surface)
        
        self._apply_transformations_and_draw(surface, game_surface, needs_mirror, needs_shake)
        
        self.draw_game_ui(surface)
        self.draw_warning_effects(surface)
        self.draw_ultimate_golden_halo(surface)
        self.draw_ultimate_transition_effects(surface)
        self.draw_difficulty_level_up(surface)
        
        if self.post_processor:
            self.post_processor.danger_flash.draw(surface)
            self.post_processor.upgrade_flash.draw(surface)
        
        if self.paused:
            self.draw_pause_screen(surface, mouse_pos)
    
    def _apply_transformations_and_draw(self, surface, game_surface, needs_mirror, needs_shake):
        if needs_shake:
            temp_surface = self.challenge_surface
            temp_surface.fill(BLACK)
            
            if abs(self.shake_angle) > 0.01:
                rotated_surface = pygame.transform.rotate(game_surface, self.shake_angle)
                rotated_rect = rotated_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                temp_surface.blit(rotated_surface, (rotated_rect.x + self.shake_offset_x, rotated_rect.y + self.shake_offset_y))
            else:
                temp_surface.blit(game_surface, (int(self.shake_offset_x), int(self.shake_offset_y)))
            
            game_surface = temp_surface
        
        if needs_mirror:
            mirrored_surface = pygame.transform.flip(game_surface, True, False)
            surface.blit(mirrored_surface, (0, 0))
        else:
            surface.blit(game_surface, (0, 0))
