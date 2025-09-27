# open palm gesture for lockscreen control

import subprocess
import time
from typing import Optional
from .base_gesture import BaseGesture


class LockScreenGesture(BaseGesture):
    # open palm gesture that locks the laptop screen
    
    def __init__(self):
        super().__init__(
            name="lockscreen",
            cooldown=5.0,  # 5 second delay between executions
            activation_delay=1.0  # 1 second delay before first execution
        )
    
    def detect(self, landmarks) -> bool:
        """
        # detect open palm gesture
        Open palm: All fingers extended (including thumb)
        """
        if not landmarks:
            return False
            
        finger_states = self.get_finger_states(landmarks)
        
        # open palm: [1, 1, 1, 1, 1] (all fingers extended)
        return finger_states == [1, 1, 1, 1, 1]
    
    def execute(self) -> bool:
        """
        # execute lockscreen command
        """
        if not self.is_ready_to_execute():
            return False
            
        try:
            # execute lockscreen command
            self.lock_screen()
            
            self.mark_executed()
            print("Screen locked")
            return True
            
        except Exception as e:
            print(f"Failed to execute lockscreen: {e}")
            return False
    
    def lock_screen(self):
        """
        # lock the laptop screen using AppleScript
        """
        # AppleScript to lock the screen
        script = '''
        tell application "System Events"
            keystroke "q" using {command down, control down}
        end tell
        '''
        
        try:
            subprocess.run(['osascript', '-e', script], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to lock screen: {e}")
            # Fallback: try alternative method
            self.fallback_lock_screen()
    
    def fallback_lock_screen(self):
        """
        # fallback method for lockscreen
        """
        try:
            # Alternative AppleScript approach
            script = '''
            tell application "System Events"
                key code 12 using {command down, control down}
            end tell
            '''
            subprocess.run(['osascript', '-e', script], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("All lockscreen methods failed")
             