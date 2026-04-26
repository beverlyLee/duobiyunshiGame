import random
import math

class ScreenShake:
    def __init__(self):
        self.active = False
        self.intensity = 0
        self.duration = 0
        self.max_duration = 0
        self.decay = 0.95
        
        self.offset_x = 0
        self.offset_y = 0
        
        self.trauma = 0.0
        self.max_trauma = 1.0
        self.trauma_decay = 0.99
        
        self.shake_angle = 0
        self.angle_offset = 0
    
    def add_trauma(self, amount=0.3):
        self.trauma = min(self.max_trauma, self.trauma + amount)
    
    def start_shake(self, intensity=8, duration=15, decay=0.95):
        self.active = True
        self.intensity = intensity
        self.duration = duration
        self.max_duration = duration
        self.decay = decay
        self.trauma = 0.5
    
    def stop_shake(self):
        self.active = False
        self.offset_x = 0
        self.offset_y = 0
        self.angle_offset = 0
        self.trauma = 0
    
    def update(self):
        if self.active and self.duration > 0:
            self.duration -= 1
            self.intensity *= self.decay
            
            if self.duration <= 0 or self.intensity < 0.1:
                self.stop_shake()
                return (0, 0, 0)
        
        if self.trauma > 0:
            self.trauma *= self.trauma_decay
            
            if self.trauma < 0.01:
                self.trauma = 0
                self.offset_x = 0
                self.offset_y = 0
                self.angle_offset = 0
                return (0, 0, 0)
        
        if self.trauma > 0 or (self.active and self.intensity > 0):
            current_intensity = max(self.intensity, self.trauma * 15)
            
            if current_intensity > 0:
                self.shake_angle += random.uniform(0.5, 1.5) * math.pi
                
                self.offset_x = current_intensity * math.sin(self.shake_angle) * (self.trauma if self.trauma > 0 else 1)
                self.offset_y = current_intensity * math.cos(self.shake_angle * 1.3) * (self.trauma if self.trauma > 0 else 1)
                
                self.angle_offset = (current_intensity * 0.05) * math.sin(self.shake_angle * 0.7)
            else:
                self.offset_x = 0
                self.offset_y = 0
                self.angle_offset = 0
        else:
            self.offset_x = 0
            self.offset_y = 0
            self.angle_offset = 0
        
        return (self.offset_x, self.offset_y, self.angle_offset)
    
    def get_offset(self):
        return (self.offset_x, self.offset_y, self.angle_offset)
    
    def is_shaking(self):
        return self.active or self.trauma > 0


class ShakeType:
    SMALL = {"intensity": 3, "duration": 10, "trauma": 0.2}
    MEDIUM = {"intensity": 6, "duration": 15, "trauma": 0.4}
    LARGE = {"intensity": 10, "duration": 25, "trauma": 0.7}
    EXPLOSION = {"intensity": 12, "duration": 30, "trauma": 0.8}
    COLLISION = {"intensity": 8, "duration": 20, "trauma": 0.6}
    IMPACT = {"intensity": 5, "duration": 12, "trauma": 0.3}
