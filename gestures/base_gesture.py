# base class for all hand gestures

import time
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
import mediapipe as mp


class BaseGesture(ABC):
    def __init__(self, name: str, cooldown: float = 1.0, activation_delay: float = 0.5):
        self.name = name
        self.cooldown = cooldown
        self.activation_delay = activation_delay # amount of time gesture must be held before executing
        self.last_execution_time = 0
        self.is_active = False
        self.activation_time = 0
        self.has_activated = False # track if gesture has been activated
        
    def can_execute(self) -> bool:
        # check if enough time has passed since last execution
        current_time = time.time()
        return current_time - self.last_execution_time >= self.cooldown
    
    def mark_executed(self):
        # mark the gesture as executed
        self.last_execution_time = time.time()
    
    def start_gesture(self):
        # called when gesture is first detected
        if not self.is_active:
            self.is_active = True
            self.activation_time = time.time()
            self.has_activated = False
    
    def end_gesture(self):
        # called when gesture is no longer detected
        self.is_active = False
        self.activation_time = 0
        self.has_activated = False
    
    def is_ready_to_execute(self) -> bool:
        # check if gesture has been held long enough to execute
        if not self.is_active:
            return False
        
        duration = self.get_gesture_duration()
        
        # first exec, wait for delay
        if not self.has_activated:
            return duration >= self.activation_delay
        
        # use cooldown
        return self.can_execute()
    
    def get_gesture_duration(self) -> float:
        # get how long the gesture has been active
        if self.is_active:
            return time.time() - self.activation_time
        return 0
    
    @abstractmethod
    def detect(self, landmarks) -> bool:
        
        # detect if this gesture is being performed
        
        # args: landmarks: MediaPipe hand landmarks
            
        # returns: bool: True if gesture is detected
        
        pass
    
    @abstractmethod
    def execute(self) -> bool:
        
        # execute the action associated with this gesture
        
        # returns: bool: True if action was executed successfully
        
        pass
    
    def get_finger_states(self, landmarks) -> List[int]:
        
        # get the state of each finger (1 = extended, 0 = bent)
        
        # args: landmarks: MediaPipe hand landmarks
            
         # returns: List[int]: [thumb, index, middle, ring, pinky] states
        
        if not landmarks or len(landmarks) < 21:
            return [0, 0, 0, 0, 0]
        
        # get key landmark positions
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2] # thumb base
        
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        index_mcp = landmarks[5]
        
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        middle_mcp = landmarks[9]
        
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        ring_mcp = landmarks[13]
        
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        pinky_mcp = landmarks[17]
        
        fingers = []
        
        # check if the thumb tip is extended beyond the IP joint
        # for thumbs up, tip should be above IP joint
        thumb_extended = thumb_tip.y < thumb_ip.y - 0.02
        fingers.append(1 if thumb_extended else 0)
        
        # other fingers, check if tip is above the PIP joint
        # for closed fingers, tip should be below or close to PIP joint
        for tip, pip in [(index_tip, index_pip), (middle_tip, middle_pip), 
                        (ring_tip, ring_pip), (pinky_tip, pinky_pip)]:
            finger_extended = tip.y < pip.y - 0.01  # Small tolerance
            fingers.append(1 if finger_extended else 0)
        
        return fingers
    
    def is_hand_facing_camera(self, landmarks) -> bool:
        # Check if the hand is in a reasonable position for gesture detection More lenient detection that works with natural hand positions
        
        # Args: landmarks: MediaPipe hand landmarks
            
        # Returns: bool: True if hand is in good position for gesture detection
        
        if not landmarks or len(landmarks) < 21:
            return False
        
        # get key points for orientation detection
        wrist = landmarks[0]
        middle_mcp = landmarks[9] # middle finger base
        index_mcp = landmarks[5] # index finger base
        ring_mcp = landmarks[13] # ring finger base
        pinky_mcp = landmarks[17] # pinky base
        
        # calculate hand center (average of finger bases)
        hand_center_x = (index_mcp.x + middle_mcp.x + ring_mcp.x + pinky_mcp.x) / 4
        hand_center_y = (index_mcp.y + middle_mcp.y + ring_mcp.y + pinky_mcp.y) / 4
        
        # more lenient check, hand should be roughly upright and not too tilted
        # check if wrist is reasonably positioned relative to hand center
        wrist_hand_distance = abs(wrist.y - hand_center_y)
        
        # check if hand is not too tilted (wrist and hand center should be roughly aligned horizontally)
        horizontal_alignment = abs(wrist.x - hand_center_x) < 0.15
        
        # check if hand is in a reasonable vertical position (not too high or low)
        reasonable_position = 0.1 < hand_center_y < 0.9
        
        # check if hand is not too far to the sides
        reasonable_horizontal = 0.1 < hand_center_x < 0.9
        
        return horizontal_alignment and reasonable_position and reasonable_horizontal
