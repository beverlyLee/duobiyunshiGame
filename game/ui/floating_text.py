import pygame
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    YELLOW, GREEN, BLACK
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
        self._original_surf = None
        self._surf_width = 0
        self._surf_height = 0

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

        if self._original_surf is None:
            self._original_surf = self.font.render(self.text, True, self.color)
            self._original_surf = self._original_surf.convert_alpha()
            self._surf_width = self._original_surf.get_width()
            self._surf_height = self._original_surf.get_height()

        text_rect = self._original_surf.get_rect(center=(int(self.x), int(self.y)))

        if self.alpha >= 255:
            surface.blit(self._original_surf, text_rect)
        else:
            temp_surf = pygame.Surface((self._surf_width, self._surf_height), pygame.SRCALPHA)
            temp_surf.blit(self._original_surf, (0, 0))
            temp_surf.set_alpha(self.alpha)
            surface.blit(temp_surf, text_rect)


class FloatingTextManager:
    def __init__(self):
        self.floating_texts = []
        self.score_offset_index = 0
        self.max_offsets = 5
        self.offset_spacing = 60

    def add_text(self, x, y, text, color=YELLOW, duration=60, float_speed=1.5, font_size=28):
        self.floating_texts.append(FloatingText(x, y, text, color, duration, float_speed, font_size))

    def add_score_text(self, x, y, score_amount):
        offset = (self.score_offset_index - self.max_offsets // 2) * self.offset_spacing
        actual_x = x + offset
        self.add_text(actual_x, y, f"+{score_amount}", GREEN, duration=90, float_speed=1.2, font_size=32)
        self.score_offset_index = (self.score_offset_index + 1) % self.max_offsets

    def add_center_message(self, text, color=YELLOW, duration=120):
        self.add_text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, text, color, duration, float_speed=0, font_size=48)

    def update(self):
        self.floating_texts = [t for t in self.floating_texts if t.update()]

    def draw(self, surface):
        for text in self.floating_texts:
            text.draw(surface)
