import os
import pygame

_font_cache = {}
_fonts_initialized = False
_default_font = None

def _test_font_render(font, size):
    try:
        test_surface = font.render("测试分数: 123", True, (255, 255, 255))
        if test_surface.get_width() > 0 and test_surface.get_height() > 0:
            return True
        return False
    except:
        return False

def _get_default_font(size):
    global _default_font
    try:
        font = pygame.font.Font(None, size)
        return font
    except:
        return None

def get_chinese_font(size):
    global _fonts_initialized, _default_font
    if not _fonts_initialized:
        pygame.init()
        _fonts_initialized = True
        _default_font = _get_default_font(28)
    
    if size in _font_cache:
        return _font_cache[size]
    
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/SimHei.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = pygame.font.Font(font_path, size)
                if _test_font_render(font, size):
                    _font_cache[size] = font
                    return font
            except:
                continue
    
    font_names = [
        "pingfang",
        "stheitisc",
        "hiraginosansgb",
        "arialunicode",
        "simhei",
        "notosanscjk",
        "sourcehansans",
        "helvetica",
        "arial",
    ]
    
    for font_name in font_names:
        try:
            font = pygame.font.SysFont(font_name, size)
            if _test_font_render(font, size):
                _font_cache[size] = font
                return font
        except:
            continue
    
    try:
        font = pygame.font.SysFont(None, size)
        if _test_font_render(font, size):
            _font_cache[size] = font
            return font
    except:
        pass
    
    default_font = _get_default_font(size)
    if default_font:
        _font_cache[size] = default_font
        return default_font
    
    _font_cache[size] = _default_font
    return _default_font

def get_font():
    font = get_chinese_font(36)
    if font is None:
        font = get_chinese_font(28)
    return font

def get_large_font():
    font = get_chinese_font(64)
    if font is None:
        font = get_chinese_font(48)
    if font is None:
        font = get_chinese_font(36)
    return font

def get_medium_font():
    font = get_chinese_font(48)
    if font is None:
        font = get_chinese_font(36)
    return font

def get_small_font():
    return get_chinese_font(28)

def init_fonts():
    global _fonts_initialized
    if not _fonts_initialized:
        pygame.init()
        _fonts_initialized = True
