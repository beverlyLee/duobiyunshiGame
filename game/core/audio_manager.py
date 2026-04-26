import pygame
import os

class AudioManager:
    def __init__(self):
        self.mixer_initialized = False
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.mixer_initialized = True
        except Exception as e:
            print(f"音频初始化失败: {e}")
            self.mixer_initialized = False
        
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.music_playing = False
        
        self.sound_effects_enabled = self.mixer_initialized
        self.music_enabled = self.mixer_initialized
    
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        if self.mixer_initialized:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def load_sound(self, name, file_path):
        if not self.mixer_initialized:
            return False
        
        if not os.path.exists(file_path):
            return False
        
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(self.sfx_volume)
            self.sounds[name] = sound
            return True
        except Exception as e:
            print(f"加载音效失败 {file_path}: {e}")
            return False
    
    def play_sound(self, name):
        if not self.sound_effects_enabled or not self.mixer_initialized:
            return
        
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"播放音效失败 {name}: {e}")
    
    def play_music(self, file_path, loops=-1):
        if not self.music_enabled or not self.mixer_initialized:
            return
        
        if not os.path.exists(file_path):
            return
        
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
            self.music_playing = True
        except Exception as e:
            print(f"播放音乐失败: {e}")
    
    def stop_music(self):
        if self.mixer_initialized and self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def pause_music(self):
        if self.mixer_initialized and self.music_playing:
            pygame.mixer.music.pause()
    
    def resume_music(self):
        if self.mixer_initialized and self.music_playing:
            pygame.mixer.music.unpause()
    
    def toggle_sound_effects(self):
        self.sound_effects_enabled = not self.sound_effects_enabled
        return self.sound_effects_enabled
    
    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if not self.music_enabled and self.music_playing:
            self.stop_music()
        return self.music_enabled


class SoundType:
    SHOOT = "shoot"
    EXPLOSION = "explosion"
    HIT = "hit"
    POWERUP = "powerup"
    COLLISION = "collision"
    GAME_OVER = "game_over"
    LEVEL_UP = "level_up"
    COMBO = "combo"


class NullAudioManager(AudioManager):
    def __init__(self):
        super().__init__()
        self.mixer_initialized = False
    
    def set_music_volume(self, volume):
        pass
    
    def set_sfx_volume(self, volume):
        pass
    
    def load_sound(self, name, file_path):
        return False
    
    def play_sound(self, name):
        pass
    
    def play_music(self, file_path, loops=-1):
        pass
    
    def stop_music(self):
        pass
    
    def pause_music(self):
        pass
    
    def resume_music(self):
        pass
    
    def toggle_sound_effects(self):
        return False
    
    def toggle_music(self):
        return False


def get_audio_manager():
    try:
        manager = AudioManager()
        return manager
    except:
        return NullAudioManager()
