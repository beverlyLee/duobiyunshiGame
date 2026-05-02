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

POWERUP_SHIELD = "shield"
POWERUP_BULLET = "bullet"
POWERUP_SLOW = "slow"

SHIELD_BLUE = (50, 150, 255)
BULLET_YELLOW = (255, 215, 0)
SLOW_GREEN = (50, 205, 50)

PENETRATING_PURPLE = (148, 0, 211)
FREEZE_CYAN = (0, 255, 255)
ICE_BLUE = (135, 206, 250)
BLUE_YELLOW_MIX = (200, 200, 100)
ENERGY_SHIELD_PURPLE = (138, 43, 226)
ENERGY_SHIELD_LIGHT_PURPLE = (186, 85, 211)
ULTIMATE_GOLD = (255, 215, 0)
ULTIMATE_LIGHT_GOLD = (255, 248, 220)

POWERUP_CONFIG = {
    POWERUP_SHIELD: {
        "color": SHIELD_BLUE,
        "symbol": "盾",
        "name": "护盾激活！",
        "duration": FPS * 5,
        "icon": "🛡️",
    },
    POWERUP_BULLET: {
        "color": BULLET_YELLOW,
        "symbol": "弹",
        "name": "子弹模式！",
        "duration": FPS * 10,
        "icon": "⚡",
    },
    POWERUP_SLOW: {
        "color": SLOW_GREEN,
        "symbol": "慢",
        "name": "陨石减速！",
        "duration": FPS * 7,
        "icon": "⏱️",
    }
}

SYNERGY_CONFIG = {
    "penetrating": {
        "name": "穿透护盾！",
        "color": BLUE_YELLOW_MIX,
        "penetration_count": 3,
        "size_multiplier": 1.2,
    },
    "freeze": {
        "name": "冰冻子弹！",
        "color": ICE_BLUE,
        "freeze_duration": FPS * 1,
        "freeze_chance": 0.3,
    },
    "energy_shield": {
        "name": "能量护盾！",
        "color": ENERGY_SHIELD_PURPLE,
        "duration_extension": FPS * 3,
        "shockwave_radius": 40,
        "knockback_force": 30,
    },
    "ultimate": {
        "name": "终极模式！",
        "color": ULTIMATE_GOLD,
        "duration": FPS * 7,
        "bullet_damage_multiplier": 3,
        "meteor_speed_multiplier": 0.25,
    }
}

METEOR_SMALL = "small"
METEOR_MEDIUM = "medium"
METEOR_LARGE = "large"
METEOR_SPLIT = "split"
METEOR_TRACKER = "tracker"
METEOR_ARMORED = "armored"
METEOR_EXPLOSIVE = "explosive"

METEOR_LIGHT_BROWN = (205, 133, 63)
METEOR_BROWN = (139, 69, 19)
METEOR_DARK_BROWN = (101, 67, 33)
METEOR_RED_BROWN = (178, 34, 34)
METEOR_PURPLE = (138, 43, 226)
METEOR_DARK_PURPLE = (75, 0, 130)
METEOR_DARK_GRAY = (64, 64, 64)
METEOR_SILVER = (192, 192, 192)
METEOR_ORANGE = (255, 140, 0)
METEOR_RED_ORANGE = (255, 69, 0)
METEOR_GREEN = (34, 139, 34)
METEOR_LIGHT_GREEN = (144, 238, 144)
METEOR_BRIGHT_RED = (255, 0, 0)

SPECIAL_METEOR_CONFIG = {
    METEOR_TRACKER: {
        "min_level": 3,
        "per_level_min": 2,
        "per_level_max": 4,
        "colors": [
            (METEOR_PURPLE, METEOR_DARK_PURPLE),
            (METEOR_GREEN, METEOR_LIGHT_GREEN)
        ]
    },
    METEOR_ARMORED: {
        "min_level": 5,
        "per_level_min": 1,
        "per_level_max": 3,
    },
    METEOR_EXPLOSIVE: {
        "min_level": 7,
        "per_level_min": 1,
        "per_level_max": 2,
    }
}

def darken_color(color, factor=0.6):
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor)
    )

def darken_color_gradient(color, hp, max_hp):
    damage_ratio = 1 - (hp / max_hp)
    darken_factor = 1 - (damage_ratio * 0.5)
    return darken_color(color, darken_factor)

METEOR_CONFIG = {
    METEOR_SMALL: {
        "name": "小型陨石",
        "width_range": (20, 30),
        "height_range": (20, 30),
        "speed_range": (6, 10),
        "hp": 1,
        "color": METEOR_LIGHT_BROWN,
        "color_inner": (222, 184, 135),
        "weight": 35,
        "score": 5,
    },
    METEOR_MEDIUM: {
        "name": "中型陨石",
        "width_range": (35, 50),
        "height_range": (35, 50),
        "speed_range": (4, 7),
        "hp": 2,
        "color": METEOR_BROWN,
        "color_inner": (160, 82, 45),
        "weight": 30,
        "score": 10,
    },
    METEOR_LARGE: {
        "name": "大型陨石",
        "width_range": (55, 75),
        "height_range": (55, 75),
        "speed_range": (2, 4),
        "hp": 3,
        "color": METEOR_DARK_BROWN,
        "color_inner": (139, 90, 43),
        "weight": 20,
        "score": 20,
    },
    METEOR_SPLIT: {
        "name": "分裂陨石",
        "width_range": (40, 55),
        "height_range": (40, 55),
        "speed_range": (3, 6),
        "hp": 2,
        "color": METEOR_RED_BROWN,
        "color_inner": (205, 92, 92),
        "weight": 15,
        "score": 15,
        "split_count": (2, 3),
        "split_type": METEOR_SMALL,
    },
    METEOR_TRACKER: {
        "name": "追踪陨石",
        "width_range": (25, 35),
        "height_range": (25, 35),
        "speed_range": (2, 4),
        "hp": 2,
        "color": METEOR_PURPLE,
        "color_inner": METEOR_DARK_PURPLE,
        "weight": 0,
        "score": 15,
        "tracking_speed": 1.0,
        "tracking_start_y": 150,
        "is_circular": True,
        "split_count": (2, 3),
        "split_type": METEOR_SMALL,
        "split_score": 5,
    },
    METEOR_ARMORED: {
        "name": "装甲陨石",
        "width_range": (45, 65),
        "height_range": (45, 65),
        "speed_range": (2, 4),
        "hp": 5,
        "armor": 0,
        "color": METEOR_DARK_GRAY,
        "color_inner": (105, 105, 105),
        "armor_color": METEOR_SILVER,
        "weight": 0,
        "score": 30,
        "metal_texture": True,
        "bullet_damage_reduction": 0.5,
    },
    METEOR_EXPLOSIVE: {
        "name": "爆炸陨石",
        "width_range": (30, 45),
        "height_range": (30, 45),
        "speed_range": (3, 5),
        "hp": 2,
        "color": METEOR_BRIGHT_RED,
        "color_inner": METEOR_RED_ORANGE,
        "weight": 0,
        "score": 20,
        "chain_explosion_bonus": 5,
        "explosion_radius": 50,
        "explosion_damage": 2,
        "fuse_time": 120,
        "glow_color": METEOR_ORANGE,
    }
}

SKILL_TREE_COLOR = {
    "ATTACK": (255, 100, 100),
    "DEFENSE": (100, 150, 255),
    "MOBILITY": (100, 255, 150),
    "UNLOCKED": (255, 215, 0),
    "LOCKED": (80, 80, 80),
    "AVAILABLE": (100, 200, 255),
    "MAXED": (255, 215, 0),
    "HOVER": (255, 255, 100),
}

SKILL_NODE_SIZE = 50
SKILL_NODE_RADIUS = 25
SKILL_ROW_SPACING = 80
SKILL_BRANCH_WIDTH = 220

EXPLOSION_ORANGE = (255, 140, 0)
EXPLOSION_LIGHT_ORANGE = (255, 180, 50)
EXPLOSION_YELLOW = (255, 255, 0)
EXPLOSION_GOLD = (255, 215, 0)
EXPLOSION_RED = (255, 50, 0)
EXPLOSION_DARK_RED = (200, 0, 0)
EXPLOSION_BRIGHT_RED = (255, 0, 0)

BULLET_TRAIL_YELLOW = (255, 255, 100)
BULLET_TRAIL_ORANGE = (255, 200, 50)
RAINBOW_COLORS = [
    (255, 0, 0), (255, 127, 0), (255, 255, 0),
    (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
]

METEOR_SMALL_PARTICLE_COUNT = 10
METEOR_MEDIUM_PARTICLE_COUNT = 20
METEOR_LARGE_PARTICLE_COUNT = 30

METEOR_PARTICLE_CONFIG = {
    METEOR_SMALL: {
        "base_count": 10,
        "size_multiplier": 0.8
    },
    METEOR_MEDIUM: {
        "base_count": 20,
        "size_multiplier": 1.0
    },
    METEOR_LARGE: {
        "base_count": 30,
        "size_multiplier": 1.3
    },
    METEOR_SPLIT: {
        "base_count": 20,
        "size_multiplier": 1.0
    },
    METEOR_TRACKER: {
        "base_count": 15,
        "size_multiplier": 0.9
    },
    METEOR_ARMORED: {
        "base_count": 25,
        "size_multiplier": 1.2
    },
    METEOR_EXPLOSIVE: {
        "base_count": 35,
        "size_multiplier": 1.5
    }
}

HIGH_COMBO_THRESHOLD = 20

POST_PROCESS_CONFIG = {
    "motion_blur": {
        "enabled": True,
        "speed_threshold": 5.0,
        "intensity": 0.3
    },
    "color_boost": {
        "enabled": True,
        "saturation_base": 1.0,
        "saturation_high_combo": 1.5,
        "combo_threshold": 20
    },
    "danger_flash": {
        "enabled": True,
        "low_hp_threshold": 1,
        "flash_interval": 30,
        "red_tint_alpha": 50
    },
    "upgrade_flash": {
        "enabled": True,
        "duration": 60,
        "gold_tint_alpha": 80
    }
}

ENVIRONMENT_CONFIG = {
    "meteors": {
        "enabled": True,
        "spawn_chance": 0.005,
        "min_speed": 8,
        "max_speed": 15,
        "min_length": 50,
        "max_length": 150
    },
    "nebula": {
        "enabled": True,
        "layer_count": 3,
        "color_palette": [
            (100, 50, 150), (50, 100, 150), (150, 100, 50)
        ],
        "move_speed": 0.1,
        "alpha_base": 30
    },
    "solar_flare": {
        "enabled": True,
        "spawn_chance": 0.001,
        "duration": 30,
        "peak_intensity": 200,
        "fade_in_frames": 5,
        "fade_out_frames": 25
    }
}

