import pygame
from game.config import WHITE, BLACK
from game.core.utils import get_small_font

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE, border_radius=15):
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
        self.border_radius = border_radius
        
        self.scale_factor = 1.0
        self.target_scale = 1.0
        self.hover_scale = 1.05
        
        self.pulse_timer = 0
        self.pulse_speed = 0.05
        
        self.is_hovered = False
        self.is_pressed = False
        self.press_scale = 0.95
        
        self.glow_intensity = 0
        self.target_glow = 0
        
        self.alpha = 255
        self.target_alpha = 255
        
        self.font_cache = {}
    
    def get_font(self, size):
        if size not in self.font_cache:
            from game.core.utils import get_font
            self.font_cache[size] = get_font()
        return self.font_cache[size]
    
    def update_scale(self):
        if self.is_pressed:
            self.target_scale = self.press_scale
        elif self.is_hovered:
            self.target_scale = self.hover_scale
        else:
            self.target_scale = 1.0
        
        scale_diff = self.target_scale - self.scale_factor
        self.scale_factor += scale_diff * 0.15
        
        if abs(self.scale_factor - self.target_scale) < 0.001:
            self.scale_factor = self.target_scale
        
        new_width = int(self.original_width * self.scale_factor)
        new_height = int(self.original_height * self.scale_factor)
        new_x = self.original_x - (new_width - self.original_width) // 2
        new_y = self.original_y - (new_height - self.original_height) // 2
        self.rect = pygame.Rect(new_x, new_y, new_width, new_height)
    
    def update_glow(self):
        if self.is_hovered:
            self.target_glow = 0.8
        else:
            self.target_glow = 0
        
        glow_diff = self.target_glow - self.glow_intensity
        self.glow_intensity += glow_diff * 0.1
    
    def create_gradient_surface(self, width, height, color, darker_factor=0.7):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        darker_color = (
            int(color[0] * darker_factor),
            int(color[1] * darker_factor),
            int(color[2] * darker_factor)
        )
        
        for y in range(height):
            progress = y / height
            r = int(color[0] * (1 - progress) + darker_color[0] * progress)
            g = int(color[1] * (1 - progress) + darker_color[1] * progress)
            b = int(color[2] * (1 - progress) + darker_color[2] * progress)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        return surface
    
    def draw_glow(self, surface):
        if self.glow_intensity <= 0:
            return
        
        glow_size = int(self.original_width * 0.15)
        glow_rect = pygame.Rect(
            self.rect.x - glow_size,
            self.rect.y - glow_size,
            self.rect.width + glow_size * 2,
            self.rect.height + glow_size * 2
        )
        
        glow_alpha = int(100 * self.glow_intensity)
        
        for i in range(glow_size, 0, -2):
            alpha = int(glow_alpha * (1 - i / glow_size))
            if alpha <= 0:
                continue
            
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surface,
                (*self.current_color, alpha),
                (i, i, glow_rect.width - i * 2, glow_rect.height - i * 2),
                border_radius=self.border_radius
            )
            surface.blit(glow_surface, glow_rect.topleft)
    
    def draw(self, surface, mouse_pos, pressed=False):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.is_pressed = pressed and self.is_hovered
        
        if self.is_hovered:
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
        
        self.update_scale()
        self.update_glow()
        
        if self.glow_intensity > 0:
            self.draw_glow(surface)
        
        button_surface = self.create_gradient_surface(
            self.rect.width, 
            self.rect.height, 
            self.current_color
        )
        
        rounded_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(rounded_surface, (255, 255, 255, 255), 
                         (0, 0, self.rect.width, self.rect.height), 
                         border_radius=self.border_radius)
        
        final_button = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        final_button.blit(button_surface, (0, 0))
        final_button.blit(rounded_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        surface.blit(final_button, self.rect.topleft)
        
        highlight_alpha = 40 if self.is_hovered else 20
        highlight_surface = pygame.Surface(
            (self.rect.width - 10, self.rect.height // 2 - 5),
            pygame.SRCALPHA
        )
        pygame.draw.rect(
            highlight_surface,
            (255, 255, 255, highlight_alpha),
            (0, 0, self.rect.width - 10, self.rect.height // 2 - 5),
            border_radius=self.border_radius // 2
        )
        surface.blit(highlight_surface, (self.rect.x + 5, self.rect.y + 3))
        
        border_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        border_alpha = 150 if self.is_hovered else 100
        pygame.draw.rect(
            border_surface,
            (255, 255, 255, border_alpha),
            (0, 0, self.rect.width, self.rect.height),
            2,
            border_radius=self.border_radius
        )
        surface.blit(border_surface, self.rect.topleft)
        
        text_size = int(self.original_height * 0.45)
        text_surf = get_small_font().render(self.text, True, self.text_color)
        
        if self.is_pressed:
            text_rect = text_surf.get_rect(
                center=(self.rect.centerx, self.rect.centery + 2)
            )
        else:
            text_rect = text_surf.get_rect(center=self.rect.center)
        
        if self.is_hovered:
            shadow_surf = get_small_font().render(self.text, True, (0, 0, 0, 100))
            shadow_rect = text_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            temp_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            temp_surf.blit(shadow_surf, (shadow_rect.x - self.rect.x, shadow_rect.y - self.rect.y))
            surface.blit(temp_surf, self.rect.topleft)
        
        surface.blit(text_surf, text_rect)
    
    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.rect.collidepoint(mouse_pos) and mouse_clicked
