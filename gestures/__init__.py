"""
AirCommand Gesture Recognition System
"""

from .base_gesture import BaseGesture
from .volume_up_gesture import VolumeUpGesture
from .volume_down_gesture import VolumeDownGesture

# Gesture registry - add new gestures here
AVAILABLE_GESTURES = {
    'volume_up': VolumeUpGesture,
    'volume_down': VolumeDownGesture,
}

def get_gesture(gesture_name: str) -> BaseGesture:
    """Get a gesture instance by name"""
    if gesture_name not in AVAILABLE_GESTURES:
        raise ValueError(f"Unknown gesture: {gesture_name}")
    return AVAILABLE_GESTURES[gesture_name]()

def list_gestures():
    """List all available gestures"""
    return list(AVAILABLE_GESTURES.keys())
