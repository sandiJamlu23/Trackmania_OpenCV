import cv2
import numpy as np
import time
import pydirectinput
import threading
from datetime import datetime
import os
import mss
import nbimporter

# Import your Lane class implementation
# Assuming the Lane class is in a file called lane_detection.py
# from comprehensive_lane import Lane, EdgeDetection
from lane_detection import Lane, EdgeDetection  # Adjust the path as needed

class AutoDriver:
    def __init__(self, screen_region=None):
        """
        Initialize the autonomous driving system.
        
        :param screen_region: Region of the screen to capture (x, y, width, height)
                             If None, will use a default region
        """
        # Initialize screen capture region
        if screen_region is None:
            # Default to a region in the center of the screen - adjust as needed
            self.screen_region = {'top': 300, 'left': 0, 'width': 800, 'height': 600}
        else:
            self.screen_region = screen_region
            
        # For screen capture
        self.sct = mss.mss()
        
        # Control parameters
        self.steering_sensitivity = 0.5  # Adjust based on testing
        self.speed_control = 0.7  # Adjust throttle sensitivity
        self.center_threshold = 10  # cm threshold for considering "centered"
        
        # State tracking
        self.is_running = False
        self.current_speed = 0  # Track current speed state
        self.current_steering = 0  # Track current steering state (-1 left, 0 center, 1 right)
        self.last_control_time = time.time()
        self.control_delay = 0.05  # Minimum time between control adjustments
        
        # Thread for continuous driving
        self.drive_thread = None

        # Direction keys configuration
        self.keys = {
            'forward': 'w',
            'backward': 's',
            'left': 'a',
            'right': 'd',
            'brake': 'space'
        }
        
        # Debug mode
        self.debug = True
        self.save_debug_frames = True
        self.debug_dir = "debug_frames"
        
        # Create debug directory if it doesn't exist
        if self.save_debug_frames and not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
            
        # Lane detection parameters
        self.edge_detector = EdgeDetection()
        
    def capture_screen(self):
        """Capture the current screen and convert to a format suitable for OpenCV"""
        # Capture the screen
        sct_img = self.sct.grab(self.screen_region)
        
        # Convert to numpy array
        img = np.array(sct_img)
        
        # Convert BGRA to BGR (remove alpha channel)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    def detect_lanes(self, frame):
        """
        Detect lanes in the given frame and return lane information
        
        :param frame: BGR image frame
        :return: Lane object with detected lanes
        """
        # Create a Lane object with the captured frame
        lane_obj = Lane(orig_frame=frame)
        
        # Process the frame for lane detection
        lane_obj.get_line_markings()
        lane_obj.perspective_transform()
        lane_obj.calculate_histogram()
        
        try:
            # Try using the sliding window method for initial lane detection
            left_fit, right_fit = lane_obj.get_lane_line_indices_sliding_windows()
            
            # Get lane line using previous window
            lane_obj.get_lane_line_previous_window(left_fit, right_fit)
            
            # Calculate curvature and position
            lane_obj.calculate_curvature()
            center_offset = lane_obj.calculate_car_position()
            
            # Calculate curve radius (average of left and right curves)
            curve_radius = (lane_obj.left_curvem + lane_obj.right_curvem) / 2
            
            return {
                'success': True,
                'lane_obj': lane_obj,
                'center_offset': center_offset,
                'curve_radius': curve_radius
            }
        except Exception as e:
            if self.debug:
                print(f"Lane detection failed: {e}")
            return {
                'success': False,
                'lane_obj': lane_obj,
                'error': str(e)
            }
    
    def control_steering(self, center_offset, curve_radius):
        """
        Determine steering input based on center offset and curve radius
        
        :param center_offset: Offset from center in cm (negative = left of center)
        :param curve_radius: Radius of curvature in meters
        :return: steering_value (-1 to 1, where -1 is full left, 1 is full right)
        """
        # Base steering on center offset
        steering_value = center_offset / 100.0  # Convert to a -1 to 1 scale
        
        # Limit the steering value
        steering_value = max(-1.0, min(1.0, steering_value * self.steering_sensitivity))
        
        # Adjust steering based on curvature (when curve is detected)
        if curve_radius < 500:  # If curve is tight
            # Add more steering in the direction of the curve
            curve_factor = 500 / max(curve_radius, 50)  # Prevent division by zero
            curve_factor = min(curve_factor, 2.0)  # Limit the curve factor
            
            # Curve direction (negative curve radius = left curve)
            if center_offset < 0:  # Left curve
                steering_value -= curve_factor * 0.1
            else:  # Right curve
                steering_value += curve_factor * 0.1
                
        return steering_value
    
    def control_speed(self, curve_radius, center_offset):
        """
        Determine speed based on curve radius and center offset
        
        :param curve_radius: Radius of curvature in meters
        :param center_offset: Offset from center in cm
        :return: speed_value (0 to 1, where 0 is stopped, 1 is full throttle)
        """
        # Base speed value
        speed_value = self.speed_control
        
        # Reduce speed in curves or when off-center
        if curve_radius < 300:
            # Slower in tight curves
            curve_factor = min(1.0, curve_radius / 300)
            speed_value *= curve_factor
            
        # Reduce speed when off-center
        center_factor = 1.0 - (min(abs(center_offset), 50) / 50) * 0.5
        speed_value *= center_factor
        
        return max(0.3, speed_value)  # Ensure minimum speed
        
    def apply_controls(self, steering_value, speed_value):
        """
        Apply steering and speed controls using pydirectinput
        
        :param steering_value: Value between -1 (full left) and 1 (full right)
        :param speed_value: Value between 0 (stop) and 1 (full throttle)
        """
        # Check if enough time has passed since last control adjustment
        current_time = time.time()
        if current_time - self.last_control_time < self.control_delay:
            return
            
        self.last_control_time = current_time
        
        # Reset all keys first (to avoid getting stuck)
        self.reset_controls()
        
        # Apply steering
        if steering_value < -0.1:  # Turn left
            pydirectinput.keyDown(self.keys['left'])
            self.current_steering = -1
        elif steering_value > 0.1:  # Turn right
            pydirectinput.keyDown(self.keys['right'])
            self.current_steering = 1
        else:
            # Centered, no steering input needed
            self.current_steering = 0
            
        # Apply throttle/speed
        if speed_value > 0.1:
            pydirectinput.keyDown(self.keys['forward'])
            self.current_speed = speed_value
        else:
            # Apply brake if we need to stop
            pydirectinput.keyDown(self.keys['brake'])
            self.current_speed = 0
    
    def reset_controls(self):
        """Reset all control inputs"""
        pydirectinput.keyUp(self.keys['forward'])
        pydirectinput.keyUp(self.keys['backward'])
        pydirectinput.keyUp(self.keys['left'])
        pydirectinput.keyUp(self.keys['right'])
        pydirectinput.keyUp(self.keys['brake'])
    
    def drive_loop(self):
        """Main driving loop that captures screen, detects lanes, and controls the car"""
        frame_count = 0
        
        while self.is_running:
            start_time = time.time()
            
            # Capture the screen
            frame = self.capture_screen()
            
            # Detect lanes
            result = self.detect_lanes(frame)
            
            if result['success']:
                # Extract lane information
                lane_obj = result['lane_obj']
                center_offset = result['center_offset']
                curve_radius = result['curve_radius']
                
                # Determine steering and speed
                steering_value = self.control_steering(center_offset, curve_radius)
                speed_value = self.control_speed(curve_radius, center_offset)
                
                # Apply controls
                self.apply_controls(steering_value, speed_value)
                
                if self.debug:
                    # Overlay lane visualization on frame
                    display_frame = lane_obj.overlay_lane_lines()
                    display_frame = lane_obj.display_curvature_offset(frame=display_frame)
                    
                    # Add driving information
                    cv2.putText(display_frame, f"Steering: {steering_value:.2f}", 
                              (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv2.putText(display_frame, f"Speed: {speed_value:.2f}", 
                              (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    
                    # Display the frame
                    cv2.imshow("Lane Detection Driver", display_frame)
                    
                    # Save debug frames every 10 frames
                    if self.save_debug_frames and frame_count % 10 == 0:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                        filename = f"{self.debug_dir}/frame_{timestamp}.jpg"
                        cv2.imwrite(filename, display_frame)
            else:
                if self.debug:
                    print("Lane detection failed, maintaining current controls")
                    cv2.imshow("Lane Detection Driver", frame)
            
            # Process key presses
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                self.stop()
                break
                
            # Calculate FPS
            frame_count += 1
            fps = 1.0 / (time.time() - start_time)
            if self.debug and frame_count % 10 == 0:
                print(f"FPS: {fps:.2f}")
    
    def start(self):
        """Start the autonomous driving system"""
        if not self.is_running:
            self.is_running = True
            self.drive_thread = threading.Thread(target=self.drive_loop)
            self.drive_thread.daemon = True
            self.drive_thread.start()
            print("Autonomous driving started")
    
    def stop(self):
        """Stop the autonomous driving system"""
        if self.is_running:
            self.is_running = False
            self.reset_controls()
            
            if self.drive_thread:
                self.drive_thread.join(timeout=1.0)
                
            cv2.destroyAllWindows()
            print("Autonomous driving stopped")
            
    def __del__(self):
        """Clean up resources when object is destroyed"""
        self.stop()
        self.sct.close()


def main():
    """Main function to run the auto driver"""
    # Define screen region to capture (adjust as needed)
    screen_region = {'top': 30, 'left': 0, 'width': 800, 'height': 600}
    
    # Create auto driver instance
    driver = AutoDriver(screen_region)
    
    # Give user time to switch to game window
    print("Starting in 3 seconds. Switch to your game window...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # Start driving
    driver.start()
    
    # Keep the main thread alive
    try:
        while driver.is_running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        driver.stop()
        print("Exited safely")


if __name__ == "__main__":
    main()