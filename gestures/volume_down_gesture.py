# thumbs down gesture for volume down control

import subprocess
import time
from typing import Optional
from .base_gesture import BaseGesture


class VolumeDownGesture(BaseGesture):
    # thumbs down gesture that decreases system volume
    
    def __init__(self):
        super().__init__(
            name="volume_down",
            cooldown=0.6, # 600ms delay between volume changes
            activation_delay=0.2 # 200ms delay before first execution
        )
        self.volume_step = 5 # volume decrement per gesture
        self.min_volume = 0 # minimum volume
        
    def detect(self, landmarks) -> bool:
        # detect thumbs down gesture like 👎 emoji
        # thumbs down: All fingers closed, thumb pointing downward
        if not landmarks:
            return False
            
        finger_states = self.get_finger_states(landmarks)
        # thumbs down: [0, 0, 0, 0, 0] (all fingers closed)
        # but thumb is extended downward (like 👎 emoji)
        if finger_states == [0, 0, 0, 0, 0]: # all fingers closed
            # check if thumb is pointing downward (thumb tip below thumb IP)
            thumb_tip = landmarks[4]
            thumb_ip = landmarks[3]
            thumb_pointing_down = thumb_tip.y > thumb_ip.y + 0.01 # more lenient threshold so thumb does not need to be perfectly straight
            
            if thumb_pointing_down:
                return True
        
        return False
    
    def execute(self) -> bool:
        # execute volume down command with macOS-style overlay
        if not self.is_ready_to_execute():
            return False
            
        try:
            # get current volume
            current_volume = self._get_current_volume()
            if current_volume is None:
                return False
            
            # calculate new volume
            new_volume = max(current_volume - self.volume_step, self.min_volume)
            
            # set new volume
            self._set_volume(new_volume)
            
            self.mark_executed()
            print(f"Volume down: {current_volume}% → {new_volume}%")
            return True
            
        except Exception as e:
            print(f"Failed to execute volume down: {e}")
            return False
    
    def _get_current_volume(self) -> Optional[int]:
        # get current system volume percentage
        try:
            result = subprocess.run([
                'osascript', '-e', 
                'output volume of (get volume settings)'
            ], capture_output=True, text=True, check=True)
            
            return int(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            return None
    
    def _set_volume(self, volume: int):
        # set system volume
        subprocess.run([
            'osascript', '-e', 
            f'set volume output volume {volume}'
        ], check=True)
    
