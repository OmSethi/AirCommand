import cv2
import mediapipe as mp
from gestures import get_gesture, list_gestures

class AirCommandController:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Initialize gestures
        self.gestures = {}
        for gesture_name in list_gestures():
            self.gestures[gesture_name] = get_gesture(gesture_name)
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Camera could not be opened")
        
        # Current active gesture
        self.current_gesture = None
        
    def run(self):
        """Main application loop"""
        print("🎯 AirCommand - Hand Gesture Control")
        print("Available gestures:")
        for name, gesture in self.gestures.items():
            print(f"  {gesture.name}: {gesture.__class__.__doc__ or 'No description'}")
        print("\nPress 'q' to quit, 'ESC' to exit")
        
        while True:
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Process image
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image)

            # Draw hand annotations and detect gestures
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks
                    self.mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Detect and execute gestures
                    self._process_gestures(hand_landmarks.landmark, image)
            
            # Flip image first, then draw status text
            image = cv2.flip(image, 1)
            
            # Display status (now on the flipped image)
            self._draw_status(image)
            
            # Show frame
            cv2.imshow('AirCommand - Hand Gesture Control', image)
            
            # Handle key presses
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
        
        self.cleanup()
    
    def _process_gestures(self, landmarks, image):
        """Process all gestures and execute active ones"""
        detected_gesture = None
        
        # Check each gesture
        for name, gesture in self.gestures.items():
            if gesture.detect(landmarks):
                detected_gesture = name
                break
        
        # Handle gesture state changes
        if detected_gesture != self.current_gesture:
            # End previous gesture
            if self.current_gesture:
                self.gestures[self.current_gesture].end_gesture()
            
            # Start new gesture
            if detected_gesture:
                self.gestures[detected_gesture].start_gesture()
                self.current_gesture = detected_gesture
            else:
                self.current_gesture = None
        
        # Execute current gesture
        if self.current_gesture:
            gesture = self.gestures[self.current_gesture]
            if gesture.execute():
                if not gesture.has_activated:
                    gesture.has_activated = True  # Mark as activated after first execution
                # Continue executing while gesture is held (cooldown handled in base class)
    
    def _draw_status(self, image):
        """Draw status information on the frame"""
        # Draw current gesture status in top left
        if self.current_gesture:
            gesture = self.gestures[self.current_gesture]
            duration = gesture.get_gesture_duration()
            
            # Color based on readiness
            if gesture.is_ready_to_execute():
                color = (0, 255, 0)  # Green - ready to execute
                status = "READY"
            else:
                color = (0, 255, 255)  # Yellow - waiting
                status = "WAITING"
            
            cv2.putText(image, f"Active: {gesture.name} ({status})", 
                      (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                      0.7, color, 2)
            cv2.putText(image, f"Duration: {duration:.1f}s", 
                      (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                      0.7, color, 2)
        else:
            cv2.putText(image, "No gesture detected", 
                      (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                      0.7, (100, 100, 100), 2)
    
    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        controller = AirCommandController()
        controller.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have a camera connected and the required permissions.")