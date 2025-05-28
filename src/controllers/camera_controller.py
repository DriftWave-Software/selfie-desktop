import cv2
import numpy as np
import time
import threading
import os
from typing import Optional, List, Tuple
from datetime import datetime

class CameraController:
    """Camera controller for handling camera operations in the SelfieBooth application."""
    
    def __init__(self):
        self.camera = None
        self.is_initialized = False
        self.camera_id = 0  # Default camera
        self.frame_width = 1280
        self.frame_height = 720
        self.preview_lock = threading.Lock()
        self.latest_frame = None
        self.video_writer = None
        self.is_recording = False
        self.recording_start_time = 0
        
        # Create output directory
        self.output_dir = os.path.join(os.path.expanduser("~"), "SelfieBooth_Media")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def initialize(self) -> bool:
        """Initialize camera and start frame capture."""
        try:
            print("Attempting to initialize camera...")
            # First try to use the real camera
            self.camera = cv2.VideoCapture(self.camera_id)
            
            if not self.camera.isOpened():
                print(f"Could not open real camera (ID: {self.camera_id}), using simulated camera instead")
                # Use a simulated camera feed (colored noise pattern)
                self._start_simulated_capture()
                self.is_initialized = True
                print("Simulated camera initialized successfully")
                return True
            
            # Set camera resolution
            print(f"Camera opened successfully, setting resolution to {self.frame_width}x{self.frame_height}")
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            
            # Check if resolution was set correctly
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Actual camera resolution: {actual_width}x{actual_height}")
            
            # Test read a frame to make sure camera is working
            ret, test_frame = self.camera.read()
            if not ret or test_frame is None:
                print("Could not read test frame from camera, using simulated camera instead")
                self.camera.release()
                self.camera = None
                self._start_simulated_capture()
                self.is_initialized = True
                print("Simulated camera initialized successfully")
                return True
            else:
                print(f"Successfully read test frame with shape: {test_frame.shape}")
                # Store this first frame so we have something to show immediately
                with self.preview_lock:
                    self.latest_frame = test_frame.copy()
            
            # Start background thread to continuously read frames
            self._start_frame_capture()
            self.is_initialized = True
            print("Real camera initialized successfully")
            
            return True
        except Exception as e:
            print(f"Camera initialization error: {e}")
            import traceback
            traceback.print_exc()
            
            # Try using simulated camera as fallback
            try:
                print("Attempting to start simulated camera as fallback...")
                self._start_simulated_capture()
                self.is_initialized = True
                print("Fallback simulated camera initialized successfully")
                return True
            except Exception as e2:
                print(f"Failed to start simulated camera: {e2}")
                return False
    
    def _start_frame_capture(self):
        """Start a background thread to continuously capture frames."""
        def capture_frames():
            frame_count = 0
            while self.is_initialized and self.camera is not None:
                try:
                    ret, frame = self.camera.read()
                    if ret:
                        # Increment frame counter and log every 30 frames (approximately once per second)
                        frame_count += 1
                        if frame_count % 30 == 0:
                            print(f"Camera captured frame #{frame_count} successfully. Shape: {frame.shape}")
                        
                        # If recording, write frame to video
                        if self.is_recording and self.video_writer:
                            self.video_writer.write(frame)
                        
                        with self.preview_lock:
                            self.latest_frame = frame
                    else:
                        print("Camera.read() returned False. Camera may be disconnected.")
                    time.sleep(0.01)  # Small sleep to avoid maxing out CPU
                except Exception as e:
                    print(f"Frame capture error: {e}")
                    time.sleep(0.1)
        
        print("Starting frame capture thread...")
        thread = threading.Thread(target=capture_frames, daemon=True)
        thread.start()
        print("Frame capture thread started")
        

        
    def _start_simulated_capture(self):
        """Start a background thread to generate simulated camera frames."""
        def generate_frames():
            width = 640
            height = 480
            frame_count = 0
            
            print("Starting simulated camera thread...")
            
            # Generate an initial frame immediately
            initial_frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add text overlay to initial frame
            text = "SIMULATED CAMERA INITIALIZING..."
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(text, font, 1, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = height // 2
            cv2.putText(initial_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2)
            
            # Store initial frame
            with self.preview_lock:
                self.latest_frame = initial_frame.copy()
                print(f"Initial simulated frame created with shape: {initial_frame.shape}")
            
            while self.is_initialized:
                try:
                    # Create a colored pattern that changes over time
                    # to simulate a camera feed
                    t = time.time() * 2  # Time factor for animation
                    frame_count += 1
                    
                    # Create a base frame with gradient
                    frame = np.zeros((height, width, 3), dtype=np.uint8)
                    
                    # Generate a colorful gradient with some movement
                    for y in range(0, height, 2):  # Step by 2 for better performance
                        for x in range(0, width, 2):  # Step by 2 for better performance
                            r = int(127 + 127 * np.sin(x / 50 + t))
                            g = int(127 + 127 * np.sin(y / 50 + t * 0.7))
                            b = int(127 + 127 * np.sin((x + y) / 100 + t * 1.3))
                            # Set 2x2 block for better performance
                            if x+1 < width and y+1 < height:
                                frame[y:y+2, x:x+2] = [b, g, r]  # OpenCV uses BGR
                    
                    # Add a text overlay
                    text = "SIMULATED CAMERA"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text_size = cv2.getTextSize(text, font, 1, 2)[0]
                    text_x = (width - text_size[0]) // 2
                    text_y = height // 2
                    cv2.putText(frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2)
                    
                    # Add frame counter
                    counter_text = f"Frame: {frame_count}"
                    cv2.putText(frame, counter_text, (10, height - 20), font, 0.5, (255, 255, 255), 1)
                    
                    # If recording, write frame to video
                    if self.is_recording and self.video_writer:
                        self.video_writer.write(frame)
                    
                    # Store the frame safely
                    with self.preview_lock:
                        self.latest_frame = frame.copy()
                    
                    # Log occasionally
                    if frame_count % 30 == 0:
                        print(f"Generated simulated frame #{frame_count}")
                    
                    time.sleep(0.033)  # ~30 FPS
                except Exception as e:
                    print(f"Simulated frame generation error: {e}")
                    import traceback
                    traceback.print_exc()
                    time.sleep(0.1)
        
        # Start the thread to generate frames
        thread = threading.Thread(target=generate_frames, daemon=True)
        thread.start()
        print("Simulated camera thread started")
    
    def get_preview_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame for preview display."""
        with self.preview_lock:
            if self.latest_frame is None:
                print("Warning: No frame available in get_preview_frame")
                return None
            
            # Print frame info occasionally
            if hasattr(self, "_frame_debug_counter"):
                self._frame_debug_counter += 1
                if self._frame_debug_counter % 30 == 0:  # Log every ~1 second
                    print(f"Returning preview frame. Shape: {self.latest_frame.shape}")
            else:
                self._frame_debug_counter = 0
                print("First frame retrieval from get_preview_frame")
            
            # Return a copy to avoid threading issues
            return self.latest_frame.copy()
        return None
    
    def capture_photo(self) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """Capture a high-quality photo frame and save it to disk."""
        if not self.is_initialized or self.camera is None:
            return None, None
        
        # For better quality, we directly read a new frame
        # rather than using the preview frame
        for _ in range(3):  # Skip a few frames to let camera adjust
            self.camera.read()
        
        ret, frame = self.camera.read()
        if not ret:
            return None, None
        
        # Save the image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert from BGR to RGB for saving
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imwrite(filepath, cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR))
        
        return frame, filepath
    
    def start_video_recording(self) -> Optional[str]:
        """Start recording video to a file."""
        if not self.is_initialized or self.camera is None or self.is_recording:
            return None
        
        try:
            # Create output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"video_{timestamp}.mp4")
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                output_path,
                fourcc,
                30.0,  # FPS
                (int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                 int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            )
            
            # Start recording
            self.is_recording = True
            self.recording_start_time = time.time()
            
            return output_path
        except Exception as e:
            print(f"Error starting video recording: {e}")
            return None
    
    def stop_video_recording(self) -> Tuple[bool, float]:
        """Stop video recording and return success status and duration."""
        if not self.is_recording or self.video_writer is None:
            return False, 0
        
        try:
            # Calculate recording duration
            duration = time.time() - self.recording_start_time
            
            # Stop recording
            self.is_recording = False
            self.video_writer.release()
            self.video_writer = None
            
            return True, duration
        except Exception as e:
            print(f"Error stopping video recording: {e}")
            return False, 0
    
    def get_recording_time(self) -> float:
        """Get the current recording duration in seconds."""
        if not self.is_recording:
            return 0
        return time.time() - self.recording_start_time
    
    def release(self):
        """Release camera resources."""
        self.is_initialized = False
        
        # Stop recording if active
        if self.is_recording and self.video_writer:
            self.stop_video_recording()
        
        # Release camera
        if self.camera is not None:
            try:
                self.camera.release()
            except Exception as e:
                print(f"Error releasing camera: {e}")
            self.camera = None
    
    def frame_to_bytes(self, frame: np.ndarray) -> bytes:
        """Convert OpenCV frame to bytes for Flet image display."""
        try:
            # Convert BGR to RGB for display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Reduce the image size for better performance if needed
            # This is especially important for iPad where large images can cause performance issues
            if frame.shape[1] > 640:  # If width > 640
                scale_factor = 640.0 / frame.shape[1]
                width = 640
                height = int(frame.shape[0] * scale_factor)
                rgb_frame = cv2.resize(rgb_frame, (width, height), interpolation=cv2.INTER_AREA)
            
            # Encode as JPEG with quality setting (0-100), lower for better performance
            encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), 80]  # 80% quality
            _, buffer = cv2.imencode('.jpg', rgb_frame, encode_params)
            
            # Return just the bytes - base64 encoding will be done in the view
            return buffer.tobytes()
        except Exception as e:
            print(f"Error converting frame to bytes: {e}")
            return b''
