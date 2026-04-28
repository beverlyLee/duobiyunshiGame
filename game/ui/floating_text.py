import pygame
import pygame.surfarray as surfarray
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    YELLOW, GREEN
)
from game.core.utils import get_chinese_font


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
        text_surf = text_surf.convert_alpha()

        if self.alpha < 255:
            alpha_ratio = self.alpha / 255.0
            alpha_array = surfarray.pixels_alpha(text_surf)
            alpha_array[:] = (alpha_array * alpha_ratio).astype(alpha_array.dtype)
            del alpha_array

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
