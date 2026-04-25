import pygame
from game.config import WHITE
from game.core.utils import get_small_font

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.original_x = x
        self.original_y = y
        self.original_width = width
        self.original_height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.scale_factor = 1.0
        self.target_scale = 1.0
        self.hover_scale = 1.08
    
    def update_scale(self, is_hovered):
        if is_hovered:
            self.target_scale = self.hover_scale
        else:
            self.target_scale = 1.0
        
        scale_diff = self.target_scale - self.scale_factor
        self.scale_factor += scale_diff * 0.2
        
        if abs(self.scale_factor - self.target_scale) < 0.001:
            self.scale_factor = self.target_scale
        
        new_width = int(self.original_width * self.scale_factor)
        new_height = int(self.original_height * self.scale_factor)
        new_x = self.original_x - (new_width - self.original_width) // 2
        new_y = self.original_y - (new_height - self.original_height) // 2
        self.rect = pygame.Rect(new_x, new_y, new_width, new_height)
    
    def draw(self, surface, mouse_pos):
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        if is_hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
        
        self.update_scale(is_hovered)
        
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surf = get_small_font().render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.rect.collidepoint(mouse_pos) and mouse_clicked
