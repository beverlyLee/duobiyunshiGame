import pygame
import os
import array
import math


class SoundType:
    SHOOT = "shoot"
    EXPLOSION = "explosion"
    HIT = "hit"
    POWERUP = "powerup"
    COLLISION = "collision"
    GAME_OVER = "game_over"
    LEVEL_UP = "level_up"
    COMBO = "combo"
    BUTTON_CLICK = "button_click"
    DODGE = "dodge"
    MOVE = "move"


class SoundGenerator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
    
    def generate_sine_wave(self, frequency, duration, volume=0.5):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            value = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
            data[i] = value
        
        return data
    
    def generate_square_wave(self, frequency, duration, volume=0.5):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            period = 1.0 / frequency
            phase = (t % period) / period
            value = int(volume * 32767 * (1 if phase < 0.5 else -1))
            data[i] = value
        
        return data
    
    def generate_sawtooth_wave(self, frequency, duration, volume=0.5):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            period = 1.0 / frequency
            phase = (t % period) / period
            value = int(volume * 32767 * (2 * phase - 1))
            data[i] = value
        
        return data
    
    def generate_white_noise(self, duration, volume=0.5):
        import random
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            value = int(volume * 32767 * (2 * random.random() - 1))
            data[i] = value
        
        return data
    
    def generate_explosion(self, duration=0.3, volume=0.7):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        import random
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration)
            noise = 2 * random.random() - 1
            
            low_freq = 100 + 50 * math.sin(2 * math.pi * 10 * t)
            low_wave = math.sin(2 * math.pi * low_freq * t)
            
            value = int(volume * fade_factor * 32767 * (0.7 * noise + 0.3 * low_wave))
            data[i] = value
        
        return data
    
    def generate_shoot(self, duration=0.15, volume=0.5):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration)
            freq = 800 - 300 * (t / duration)
            value = int(volume * fade_factor * 32767 * math.sin(2 * math.pi * freq * t))
            data[i] = value
        
        return data
    
    def generate_powerup(self, duration=0.4, volume=0.6):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration) * 0.5
            
            freq1 = 400 + 200 * math.sin(2 * math.pi * 15 * t)
            freq2 = freq1 * 1.5
            
            wave1 = math.sin(2 * math.pi * freq1 * t)
            wave2 = math.sin(2 * math.pi * freq2 * t)
            
            value = int(volume * fade_factor * 32767 * (0.5 * wave1 + 0.5 * wave2))
            data[i] = value
        
        return data
    
    def generate_collision(self, duration=0.2, volume=0.8):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        import random
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration)
            noise = 2 * random.random() - 1
            
            low_freq = 80 + 40 * math.sin(2 * math.pi * 20 * t)
            low_wave = math.sin(2 * math.pi * low_freq * t)
            
            value = int(volume * fade_factor * 32767 * (0.6 * noise + 0.4 * low_wave))
            data[i] = value
        
        return data
    
    def generate_game_over(self, duration=1.0, volume=0.7):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration) * 0.3
            
            if t < 0.3:
                freq = 400 - 200 * (t / 0.3)
            elif t < 0.6:
                freq = 200 - 100 * ((t - 0.3) / 0.3)
            else:
                freq = 100 - 50 * ((t - 0.6) / 0.4)
            
            value = int(volume * fade_factor * 32767 * math.sin(2 * math.pi * freq * t))
            data[i] = value
        
        return data
    
    def generate_level_up(self, duration=0.5, volume=0.6):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration) * 0.3
            
            note_duration = duration / 4
            
            if t < note_duration:
                freq = 440
            elif t < note_duration * 2:
                freq = 554
            elif t < note_duration * 3:
                freq = 659
            else:
                freq = 880
            
            wave1 = math.sin(2 * math.pi * freq * t)
            wave2 = math.sin(2 * math.pi * freq * 2 * t)
            
            value = int(volume * fade_factor * 32767 * (0.7 * wave1 + 0.3 * wave2))
            data[i] = value
        
        return data
    
    def generate_button_click(self, duration=0.1, volume=0.4):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration)
            freq = 1200 - 800 * (t / duration)
            value = int(volume * fade_factor * 32767 * math.sin(2 * math.pi * freq * t))
            data[i] = value
        
        return data
    
    def generate_dodge(self, duration=0.1, volume=0.3):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration)
            freq = 600 + 200 * (t / duration)
            value = int(volume * fade_factor * 32767 * math.sin(2 * math.pi * freq * t))
            data[i] = value
        
        return data
    
    def generate_hit(self, duration=0.15, volume=0.6):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        import random
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration)
            noise = 2 * random.random() - 1
            
            freq = 300 + 100 * math.sin(2 * math.pi * 50 * t)
            wave = math.sin(2 * math.pi * freq * t)
            
            value = int(volume * fade_factor * 32767 * (0.5 * noise + 0.5 * wave))
            data[i] = value
        
        return data
    
    def generate_move(self, duration=0.2, volume=0.3):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        for i in range(num_samples):
            t = i / self.sample_rate
            fade_factor = 1 - (t / duration) * 0.5
            
            freq1 = 150 + 50 * math.sin(2 * math.pi * 30 * t)
            freq2 = freq1 * 2
            
            wave1 = math.sin(2 * math.pi * freq1 * t)
            wave2 = math.sin(2 * math.pi * freq2 * t)
            
            value = int(volume * fade_factor * 32767 * (0.6 * wave1 + 0.4 * wave2))
            data[i] = value
        
        return data
    
    def create_sound(self, data):
        stereo_data = array.array('h')
        for sample in data:
            stereo_data.append(sample)
            stereo_data.append(sample)
        
        return pygame.mixer.Sound(buffer=stereo_data)
    
    def generate_background_music(self, duration=10.0, volume=0.3):
        num_samples = int(self.sample_rate * duration)
        data = array.array('h', [0]) * num_samples
        
        base_freqs = [110, 130.81, 146.83, 164.81, 174.61, 196.00, 220.00]
        melody_pattern = [0, 2, 4, 5, 4, 2, 0, 3]
        bass_pattern = [0, 0, 5, 5, 3, 3, 4, 4]
        
        beat_duration = 0.25
        samples_per_beat = int(self.sample_rate * beat_duration)
        
        for i in range(num_samples):
            beat_index = (i // samples_per_beat) % len(melody_pattern)
            beat_position = (i % samples_per_beat) / samples_per_beat
            
            note_volume = 1.0
            if beat_position < 0.1:
                note_volume = beat_position / 0.1
            elif beat_position > 0.8:
                note_volume = (1.0 - beat_position) / 0.2
            
            melody_note = melody_pattern[beat_index]
            melody_freq = base_freqs[melody_note] * 2
            melody_wave = math.sin(2 * math.pi * melody_freq * (i / self.sample_rate))
            melody_wave += 0.3 * math.sin(2 * math.pi * melody_freq * 2 * (i / self.sample_rate))
            melody_wave += 0.15 * math.sin(2 * math.pi * melody_freq * 3 * (i / self.sample_rate))
            
            bass_note = bass_pattern[beat_index]
            bass_freq = base_freqs[bass_note]
            bass_wave = math.sin(2 * math.pi * bass_freq * (i / self.sample_rate))
            bass_wave += 0.5 * math.sin(2 * math.pi * bass_freq * 2 * (i / self.sample_rate))
            
            pad_wave = 0.1 * math.sin(2 * math.pi * 55 * (i / self.sample_rate))
            pad_wave += 0.1 * math.sin(2 * math.pi * 82.41 * (i / self.sample_rate))
            pad_wave += 0.1 * math.sin(2 * math.pi * 110 * (i / self.sample_rate))
            
            combined_wave = 0.3 * melody_wave + 0.4 * bass_wave + 0.2 * pad_wave
            value = int(volume * note_volume * 32767 * combined_wave)
            
            data[i] = max(-32767, min(32767, value))
        
        return data


class AudioManager:
    def __init__(self):
        self.mixer_initialized = False
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.mixer_initialized = True
            print("音频系统初始化成功")
        except Exception as e:
            print(f"音频初始化失败: {e}")
            self.mixer_initialized = False
        
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.music_playing = False
        self.current_music = None
        
        self.background_music = None
        self.music_channel = None
        self.using_synth_music = False
        
        self.sound_effects_enabled = self.mixer_initialized
        self.music_enabled = self.mixer_initialized
        
        self.assets_path = self._find_assets_path()
        
        self.sound_generator = None
        if self.mixer_initialized:
            self.sound_generator = SoundGenerator()
    
    def _find_assets_path(self):
        possible_paths = [
            os.path.join(os.getcwd(), "assets"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return os.path.join(os.getcwd(), "assets")
    
    def _get_sound_path(self, sound_name):
        sound_files = [
            os.path.join(self.assets_path, "sounds", f"{sound_name}.wav"),
            os.path.join(self.assets_path, "sounds", f"{sound_name}.mp3"),
            os.path.join(self.assets_path, "sounds", f"{sound_name}.ogg"),
        ]
        for path in sound_files:
            if os.path.exists(path):
                return path
        return None
    
    def _get_music_path(self, music_name):
        music_files = [
            os.path.join(self.assets_path, "music", f"{music_name}.mp3"),
            os.path.join(self.assets_path, "music", f"{music_name}.wav"),
            os.path.join(self.assets_path, "music", f"{music_name}.ogg"),
        ]
        for path in music_files:
            if os.path.exists(path):
                return path
        return None
    
    def _generate_synthetic_sound(self, name):
        if not self.sound_generator:
            return None
        
        try:
            if name == SoundType.SHOOT:
                data = self.sound_generator.generate_shoot()
            elif name == SoundType.EXPLOSION:
                data = self.sound_generator.generate_explosion()
            elif name == SoundType.HIT:
                data = self.sound_generator.generate_hit()
            elif name == SoundType.POWERUP:
                data = self.sound_generator.generate_powerup()
            elif name == SoundType.COLLISION:
                data = self.sound_generator.generate_collision()
            elif name == SoundType.GAME_OVER:
                data = self.sound_generator.generate_game_over()
            elif name == SoundType.LEVEL_UP:
                data = self.sound_generator.generate_level_up()
            elif name == SoundType.BUTTON_CLICK:
                data = self.sound_generator.generate_button_click()
            elif name == SoundType.DODGE:
                data = self.sound_generator.generate_dodge()
            elif name == SoundType.MOVE:
                data = self.sound_generator.generate_move()
            else:
                data = self.sound_generator.generate_sine_wave(440, 0.1, 0.3)
            
            sound = self.sound_generator.create_sound(data)
            sound.set_volume(self.sfx_volume)
            return sound
        except Exception as e:
            print(f"生成合成音效失败 {name}: {e}")
            return None
    
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        if self.mixer_initialized:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def load_sound(self, name, file_path=None):
        if not self.mixer_initialized:
            return False
        
        if file_path is None:
            file_path = self._get_sound_path(name)
        
        if file_path is not None and os.path.exists(file_path):
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.set_volume(self.sfx_volume)
                self.sounds[name] = sound
                print(f"成功加载音效: {name} (从文件)")
                return True
            except Exception as e:
                print(f"加载音效失败 {file_path}: {e}")
        
        sound = self._generate_synthetic_sound(name)
        if sound:
            self.sounds[name] = sound
            print(f"成功加载音效: {name} (合成)")
            return True
        
        return False
    
    def load_all_sounds(self):
        if not self.mixer_initialized:
            return False
        
        sound_names = [
            SoundType.SHOOT,
            SoundType.EXPLOSION,
            SoundType.HIT,
            SoundType.POWERUP,
            SoundType.COLLISION,
            SoundType.GAME_OVER,
            SoundType.LEVEL_UP,
            SoundType.COMBO,
            SoundType.BUTTON_CLICK,
            SoundType.DODGE,
            SoundType.MOVE,
        ]
        
        loaded_count = 0
        for name in sound_names:
            if self.load_sound(name):
                loaded_count += 1
        
        if loaded_count > 0:
            print(f"成功加载 {loaded_count}/{len(sound_names)} 个音效")
        else:
            print("提示: 无法加载任何音效")
        
        return loaded_count > 0
    
    def play_sound(self, name):
        if not self.sound_effects_enabled or not self.mixer_initialized:
            return
        
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"播放音效失败 {name}: {e}")
    
    def play_music(self, music_name="background", loops=-1):
        if not self.music_enabled or not self.mixer_initialized:
            return
        
        file_path = self._get_music_path(music_name)
        
        if file_path is not None:
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                self.music_playing = True
                self.current_music = music_name
                self.using_synth_music = False
                print(f"开始播放音乐: {music_name} (从文件)")
                return
            except Exception as e:
                print(f"从文件播放音乐失败: {e}")
        
        if self.sound_generator:
            try:
                print(f"正在生成合成背景音乐: {music_name}...")
                music_data = self.sound_generator.generate_background_music(
                    duration=10.0, volume=self.music_volume * 0.6
                )
                self.background_music = self.sound_generator.create_sound(music_data)
                self.background_music.set_volume(self.music_volume)
                
                if self.music_channel is None:
                    self.music_channel = pygame.mixer.find_channel()
                
                if self.music_channel:
                    self.music_channel.play(self.background_music, loops=loops)
                    self.music_playing = True
                    self.current_music = music_name
                    self.using_synth_music = True
                    print(f"开始播放音乐: {music_name} (合成)")
                else:
                    print("警告: 无法找到可用的音频通道播放背景音乐")
            except Exception as e:
                print(f"生成合成音乐失败: {e}")
        else:
            print(f"音乐文件不存在: {music_name}，且无法生成合成音乐")
    
    def stop_music(self):
        if not self.mixer_initialized or not self.music_playing:
            return
        
        if self.using_synth_music:
            if self.music_channel:
                self.music_channel.stop()
                self.music_playing = False
                self.current_music = None
                self.background_music = None
        else:
            pygame.mixer.music.stop()
            self.music_playing = False
            self.current_music = None
    
    def pause_music(self):
        if not self.mixer_initialized or not self.music_playing:
            return
        
        if self.using_synth_music:
            if self.music_channel:
                self.music_channel.pause()
        else:
            pygame.mixer.music.pause()
    
    def resume_music(self):
        if not self.mixer_initialized or not self.music_playing:
            return
        
        if self.using_synth_music:
            if self.music_channel:
                self.music_channel.unpause()
        else:
            pygame.mixer.music.unpause()
    
    def toggle_sound_effects(self):
        self.sound_effects_enabled = not self.sound_effects_enabled
        return self.sound_effects_enabled
    
    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if not self.music_enabled and self.music_playing:
            self.stop_music()
        return self.music_enabled
    
    def is_music_playing(self):
        return self.music_playing and self.mixer_initialized
    
    def get_music_volume(self):
        return self.music_volume
    
    def get_sfx_volume(self):
        return self.sfx_volume


class NullAudioManager(AudioManager):
    def __init__(self):
        super().__init__()
        self.mixer_initialized = False
    
    def set_music_volume(self, volume):
        pass
    
    def set_sfx_volume(self, volume):
        pass
    
    def load_sound(self, name, file_path=None):
        return False
    
    def load_all_sounds(self):
        return False
    
    def play_sound(self, name):
        pass
    
    def play_music(self, music_name="background", loops=-1):
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
    
    def is_music_playing(self):
        return False
    
    def get_music_volume(self):
        return 0.5
    
    def get_sfx_volume(self):
        return 0.7


def get_audio_manager():
    try:
        manager = AudioManager()
        return manager
    except:
        return NullAudioManager()
