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

METEOR_SMALL = "small"
METEOR_MEDIUM = "medium"
METEOR_LARGE = "large"
METEOR_SPLIT = "split"

METEOR_LIGHT_BROWN = (205, 133, 63)
METEOR_BROWN = (139, 69, 19)
METEOR_DARK_BROWN = (101, 67, 33)
METEOR_RED_BROWN = (178, 34, 34)

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
    }
}
