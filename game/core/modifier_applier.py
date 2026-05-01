import pygame
from typing import List, Optional, Dict, Any, Callable
from game.core.daily_challenge import (
    ModifierType, MODIFIER_CONFIG, DailyChallenge, DailyChallengeManager, get_daily_challenge_manager
)
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class ModifierApplier:
    def __init__(self):
        self.active_modifiers: List[ModifierType] = []
        self.modifier_effects: Dict[ModifierType, Dict[str, Any]] = {}
        
        self.challenge_manager: Optional[DailyChallengeManager] = None
        self.is_challenge_mode: bool = False
        
        self._mini_scale: float = 0.7
        self._time_multiplier: float = 1.0
        self._gravity_reversed: bool = False
        self._infinite_bullets: bool = False
        self._fragile_ship: bool = False
        self._mirror_mode: bool = False
        
        self._mirror_surface: Optional[pygame.Surface] = None
        
    def initialize(self, challenge_manager: Optional[DailyChallengeManager] = None):
        self.challenge_manager = challenge_manager or get_daily_challenge_manager()
        
    def start_challenge_mode(self) -> DailyChallenge:
        challenge = self.challenge_manager.get_current_challenge()
        self.active_modifiers = challenge.modifiers
        self.is_challenge_mode = True
        self._apply_modifiers()
        return challenge
    
    def end_challenge_mode(self):
        self.active_modifiers = []
        self.is_challenge_mode = False
        self._reset_modifiers()
    
    def _apply_modifiers(self):
        for modifier in self.active_modifiers:
            self._apply_single_modifier(modifier)
    
    def _apply_single_modifier(self, modifier: ModifierType):
        if modifier == ModifierType.INFINITE_BULLETS:
            self._infinite_bullets = True
        elif modifier == ModifierType.FRAGILE_SHIP:
            self._fragile_ship = True
        elif modifier == ModifierType.ACCELERATED_TIME:
            self._time_multiplier = 1.5
        elif modifier == ModifierType.MINI_MODE:
            self._mini_scale = 0.7
        elif modifier == ModifierType.MIRROR_MODE:
            self._mirror_mode = True
            if self._mirror_surface is None:
                self._mirror_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        elif modifier == ModifierType.GRAVITY_REVERSAL:
            self._gravity_reversed = True
    
    def _reset_modifiers(self):
        self._infinite_bullets = False
        self._fragile_ship = False
        self._time_multiplier = 1.0
        self._mini_scale = 1.0
        self._mirror_mode = False
        self._gravity_reversed = False
        self._mirror_surface = None
    
    def has_modifier(self, modifier: ModifierType) -> bool:
        return modifier in self.active_modifiers
    
    def get_time_multiplier(self) -> float:
        return self._time_multiplier
    
    def is_infinite_bullets(self) -> bool:
        return self._infinite_bullets
    
    def is_fragile_ship(self) -> bool:
        return self._fragile_ship
    
    def is_mini_mode(self) -> bool:
        return self._mini_scale < 1.0
    
    def get_mini_scale(self) -> float:
        return self._mini_scale
    
    def is_mirror_mode(self) -> bool:
        return self._mirror_mode
    
    def is_gravity_reversed(self) -> bool:
        return self._gravity_reversed
    
    def apply_to_ship(self, ship):
        if self._fragile_ship:
            pass
        
        if self.is_mini_mode():
            original_width = getattr(ship, '_original_width', ship.width)
            original_height = getattr(ship, '_original_height', ship.height)
            
            if not hasattr(ship, '_original_width'):
                ship._original_width = ship.width
                ship._original_height = ship.height
            
            ship.width = int(original_width * self._mini_scale)
            ship.height = int(original_height * self._mini_scale)
            ship.rect = pygame.Rect(ship.x, ship.y, ship.width, ship.height)
    
    def apply_to_meteor(self, meteor):
        if self.is_mini_mode():
            if not hasattr(meteor, '_original_width'):
                meteor._original_width = meteor.width
                meteor._original_height = meteor.height
            
            meteor.width = int(meteor._original_width * self._mini_scale)
            meteor.height = int(meteor._original_height * self._mini_scale)
            meteor.rect = pygame.Rect(meteor.x, meteor.y, meteor.width, meteor.height)
    
    def apply_to_bullet(self, bullet):
        if self.is_mini_mode():
            if not hasattr(bullet, '_original_width'):
                bullet._original_width = bullet.width
                bullet._original_height = bullet.height
            
            bullet.width = int(bullet._original_width * self._mini_scale)
            bullet.height = int(bullet._original_height * self._mini_scale)
            bullet.rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
    
    def apply_to_powerup(self, powerup):
        if self.is_mini_mode():
            if not hasattr(powerup, '_original_width'):
                powerup._original_width = powerup.width
                powerup._original_height = powerup.height
            
            powerup.width = int(powerup._original_width * self._mini_scale)
            powerup.height = int(powerup._original_height * self._mini_scale)
            powerup.rect = pygame.Rect(powerup.x, powerup.y, powerup.width, powerup.height)
    
    def adjust_meteor_speed(self, base_speed: float) -> float:
        speed = base_speed * self._time_multiplier
        
        if self._gravity_reversed:
            speed = -speed
        
        return speed
    
    def adjust_meteor_spawn_y(self, base_y: float) -> float:
        if self._gravity_reversed:
            return SCREEN_HEIGHT
        return base_y
    
    def apply_mirror_effect(self, surface: pygame.Surface) -> pygame.Surface:
        if not self._mirror_mode:
            return surface
        
        if self._mirror_surface is None:
            self._mirror_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self._mirror_surface.blit(surface, (0, 0))
        
        mirrored = pygame.transform.flip(self._mirror_surface, True, False)
        
        return mirrored
    
    def get_active_modifier_configs(self) -> List[Dict]:
        return [{"type": m.value, **MODIFIER_CONFIG[m]} for m in self.active_modifiers]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_challenge_mode": self.is_challenge_mode,
            "active_modifiers": [m.value for m in self.active_modifiers],
            "modifier_effects": {
                "time_multiplier": self._time_multiplier,
                "infinite_bullets": self._infinite_bullets,
                "fragile_ship": self._fragile_ship,
                "mini_scale": self._mini_scale,
                "mirror_mode": self._mirror_mode,
                "gravity_reversed": self._gravity_reversed,
            }
        }


_modifier_applier_instance: Optional[ModifierApplier] = None


def get_modifier_applier() -> ModifierApplier:
    global _modifier_applier_instance
    if _modifier_applier_instance is None:
        _modifier_applier_instance = ModifierApplier()
    return _modifier_applier_instance
