import os
import pygame

_font_cache = {}
_fonts_initialized = False

def get_chinese_font(size):
    global _fonts_initialized
    if not _fonts_initialized:
        pygame.init()
        _fonts_initialized = True
    
    if size in _font_cache:
        return _font_cache[size]
    
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/SimHei.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = pygame.font.Font(font_path, size)
                _font_cache[size] = font
                return font
            except:
                continue
    
    try:
        font = pygame.font.SysFont("pingfang", size)
        _font_cache[size] = font
        return font
    except:
        try:
            font = pygame.font.SysFont("stheitisc", size)
            _font_cache[size] = font
            return font
        except:
            font = pygame.font.Font(None, size)
            _font_cache[size] = font
            return font

def get_font():
    return get_chinese_font(36)

def get_large_font():
    return get_chinese_font(64)

def get_medium_font():
    return get_chinese_font(48)

def get_small_font():
    return get_chinese_font(28)

def init_fonts():
    global _fonts_initialized
    if not _fonts_initialized:
        pygame.init()
        _fonts_initialized = True
