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
