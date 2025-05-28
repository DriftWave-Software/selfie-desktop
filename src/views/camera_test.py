import flet as ft
import threading
import time
import os
import base64
import cv2
from src.utils.api_client import APIClient
from src.components.topbar import TopBar
from src.controllers.camera_controller import CameraController

class CameraTestView(ft.View):
    def __init__(self, page: ft.Page, api_client: APIClient, event_id: str, mode: str = "photo"):
        super().__init__()
        self.page = page
        self.api_client = api_client
        self.event_id = int(event_id)
        self.mode = mode
        self.camera_controller = CameraController()
        self.is_initialized = False
        self.is_recording = False
        self.recording_timer = None
        self.recording_seconds = 0
        self.captured_media = []
        self._latest_frame_data = None
        self._preview_timer = None
        self.build()
    
    def build(self):
        """Build the camera test view UI"""
        self.route = f"/camera_test/{self.event_id}"
        self.bgcolor = "#18181b"
        self.padding = 0
        
        # Top bar with back button
        self.top_bar = TopBar(
            user_name=self.api_client.user_data.get("name", "User") if self.api_client.user_data else None,
            on_back=lambda e: self.handle_back(),
            show_back=True
        )
        
        # Camera preview
        self.camera_preview = ft.Image(
            src_base64=self._create_placeholder_image(),
            width=640,
            height=480,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10,
        )
        
        # Camera preview container
        self.preview_container = ft.Container(
            content=self.camera_preview,
            width=640,
            height=480,
            bgcolor="#000000",
            border_radius=10,
            alignment=ft.alignment.center,
        )
        
        # Status indicator
        self.status_text = ft.Text(
            "Initializing camera...", 
            color="green",  # Use string instead of ft.Colors.GREEN
            size=16,
            weight=ft.FontWeight.BOLD
        )
        
        # Camera controls
        self.capture_button = ft.ElevatedButton(
            "Take Photo",
            icon=ft.Icons.CAMERA_ALT,
            on_click=self.capture_photo,
            disabled=True,  # Initially disabled until camera is ready
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20,
                bgcolor="#4CAF50",
                color="white",
            ),
        )
        
        self.video_button = ft.ElevatedButton(
            "Record Video",
            icon=ft.Icons.VIDEOCAM,
            on_click=self.toggle_recording,
            disabled=True,  # Initially disabled until camera is ready
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20,
                bgcolor="#F44336",
                color="white",
            ),
        )
        
        self.timer_text = ft.Text("00:00", size=24, visible=False)
        
        # Controls row with buttons
        self.controls_row = ft.Row(
            [self.capture_button, self.timer_text, self.video_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        
        # Media thumbnails scrollable area
        self.thumbnails_label = ft.Text(
            "Captured Media:",
            size=16,
            weight=ft.FontWeight.BOLD,
            color="white",
        )
        
        self.thumbnails_row = ft.Row(
            scroll=ft.ScrollMode.AUTO,
            height=120,
        )
        
        self.thumbnails_container = ft.Container(
            content=ft.Column(
                [
                    self.thumbnails_label,
                    ft.Container(
                        content=self.thumbnails_row,
                        height=150,
                        width=800,
                        bgcolor="#232323",
                        border_radius=10,
                        padding=ft.padding.all(10),
                    ),
                ],
                spacing=10,
            ),
            margin=ft.margin.only(top=20),
        )
        
        # Add content to view
        self.controls = [
            ft.Column(
                controls=[
                    self.top_bar,
                    ft.Container(
                        content=ft.Column(
                            [
                                self.status_text,
                                self.preview_container,
                                self.controls_row,
                                self.thumbnails_container,
                            ],
                            spacing=20,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.all(40),
                    ),
                ],
                spacing=0,
                expand=True,
            )
        ]
        
        # Camera will be initialized when view is mounted
    
    def did_mount(self, e=None):
        """Called when the view is mounted"""
        print("CameraTestView mounted, initializing camera...")
        
        # Update status
        self.status_text.value = "Initializing camera..."
        self.page.update(self.status_text)
        
        # Start camera directly without using controller
        threading.Thread(target=self._direct_camera_preview, daemon=True).start()
        
    def _initialize_camera(self):
        """Initialize camera in background thread"""
        try:
            # Update status
            def update_status(message, success=None):
                self.status_text.value = message
                if success is not None:
                    self.status_text.color = "green" if success else "red"
                self.page.update(self.status_text)
            
            update_status("Initializing camera...", None)
            
            # Initialize camera controller
            if self.camera_controller.initialize():
                update_status("Camera initialized successfully", True)
                self.is_initialized = True
                
                # Enable camera controls
                self.capture_button.disabled = False
                self.video_button.disabled = False
                self.page.update(self.capture_button)
                self.page.update(self.video_button)
                
                # Start frame capture thread
                thread = threading.Thread(target=self._update_preview, daemon=True)
                thread.daemon = True  # Ensure thread dies with main process
                thread.start()
                
                # Set up timer to regularly update UI with latest frame
                self._setup_preview_timer()
                
                update_status("Camera ready", True)
            else:
                update_status("Failed to initialize camera", False)
        except Exception as e:
            print(f"Error initializing camera: {e}")
            import traceback
            traceback.print_exc()
            
            # Update UI with error message
            self.status_text.value = f"Camera error: {str(e)}"
            self.status_text.color = "red"
            self.page.update(self.status_text)
    
    def will_unmount(self):
        """Called when the view is about to be unmounted"""
        # Release camera resources
        if self.is_recording:
            self.toggle_recording(None)
        
        # Stop the preview timer
        if self._preview_timer and self._preview_timer.is_alive():
            self._preview_timer.cancel()
            self._preview_timer = None
        
        if self.camera_controller:
            self.camera_controller.release()
        
        self.is_initialized = False
    
    # No need for a timer - direct updates from the camera thread
    def _setup_preview_timer(self):
        """This method is kept for compatibility but doesn't do anything now"""
        print("Using direct UI updates instead of timer-based updates")
        pass
        
    def _direct_camera_preview(self):
        """Simple direct camera preview implementation - copied exactly from working debug_camera.py"""
        # Initialize variables
        frame_count = 0
        camera = None
        
        try:
            print("Starting direct camera access...")
            
            # List all possible camera indices
            print("Checking for available cameras...")
            
            # Try different camera APIs in this preferred order
            backends = [
                cv2.CAP_ANY,      # Auto-detect
                cv2.CAP_V4L2,     # Video4Linux - common on Linux
                cv2.CAP_DSHOW,    # DirectShow - Windows
                cv2.CAP_MSMF,     # Media Foundation - Windows
                cv2.CAP_AVFOUNDATION  # AVFoundation - macOS
            ]
            
            camera = None
            camera_found = False
            
            # Try camera indices 0-4 with different backends
            for backend in backends:
                for cam_id in range(5):  # Try camera IDs 0 through 4
                    try:
                        print(f"Trying camera ID {cam_id} with backend {backend}...")
                        camera = cv2.VideoCapture(cam_id, backend)
                        
                        if camera.isOpened():
                            # Try to read a test frame to confirm it works
                            ret, test_frame = camera.read()
                            if ret and test_frame is not None:
                                print(f"Successfully opened camera with ID {cam_id} using backend {backend}")
                                camera_found = True
                                break
                            else:
                                print(f"Camera {cam_id} opened but could not read frames")
                                camera.release()
                        else:
                            print(f"Could not open camera {cam_id}")
                            if camera is not None:
                                camera.release()
                    except Exception as e:
                        print(f"Error with camera {cam_id}, backend {backend}: {e}")
                        if camera is not None:
                            camera.release()
                
                if camera_found:
                    break
            
            if not camera_found or not camera.isOpened():
                # Try one more approach - system-specific device paths
                try:
                    print("Trying direct device access...")
                    # Check for system cameras
                    import subprocess
                    result = subprocess.run(['ls', '-l', '/dev/video*'], capture_output=True, text=True)
                    print(f"Available video devices:\n{result.stdout}")
                    
                    # Try the first available video device
                    if 'video' in result.stdout:
                        for line in result.stdout.split('\n'):
                            if 'video' in line:
                                device = line.split()[-1]
                                print(f"Trying direct access to {device}")
                                camera = cv2.VideoCapture(device)
                                if camera.isOpened():
                                    ret, test_frame = camera.read()
                                    if ret and test_frame is not None:
                                        print(f"Successfully opened camera with device {device}")
                                        camera_found = True
                                        break
                                    else:
                                        camera.release()
                except Exception as e:
                    print(f"Error with direct device access: {e}")
            
            if not camera_found or not camera.isOpened():
                error_msg = "Could not access any camera after trying multiple methods. Please check camera connections and permissions."
                print(error_msg)
                self.status_text.value = f"Error: {error_msg}"
                self.status_text.color = "red"
                self.page.update(self.status_text)
                return
                
            # Set camera properties
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Get actual properties
            width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = camera.get(cv2.CAP_PROP_FPS)
            
            print(f"Camera opened successfully: {width}x{height}@{fps}fps")
            
            # Update status
            self.status_text.value = "Camera ready"
            self.status_text.color = "green"
            self.page.update(self.status_text)
            
            # Enable buttons
            self.capture_button.disabled = False
            self.video_button.disabled = False
            self.page.update(self.capture_button)
            self.page.update(self.video_button)
            
            # Set initialized flag
            self.is_initialized = True
            
            # Main capture loop - this is the key part from the working debug app
            frame_count = 0
            while self.is_initialized:
                # Capture frame from real camera
                ret, frame = camera.read()
                
                if not ret or frame is None:
                    print("Failed to capture frame")
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # Convert to JPEG and then to base64 - exactly as in debug app
                _, buffer = cv2.imencode('.jpg', frame)
                img_bytes = buffer.tobytes()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # Update the UI directly - key part from debug app
                self.camera_preview.src_base64 = img_base64
                self.page.update(self.camera_preview)
                
                # Store for potential photo capture
                self.latest_frame = frame.copy()
                
                # Write frame to video if recording
                if self.is_recording and hasattr(self, 'video_writer') and self.video_writer is not None:
                    try:
                        self.video_writer.write(frame)
                    except Exception as e:
                        print(f"Error writing video frame: {e}")
                        # Don't crash the preview thread on video writing errors
                
                # Log progress occasionally
                if frame_count % 30 == 0:
                    print(f"Camera frame #{frame_count} successfully displayed")
                
                # Control frame rate
                time.sleep(0.03)  # ~33 FPS
                
        except Exception as e:
            print(f"Camera error: {e}")
            import traceback
            traceback.print_exc()
            
            # Update status
            self.status_text.value = f"Camera error: {str(e)}"
            self.status_text.color = "red"
            self.page.update(self.status_text)
            
        finally:
            # Clean up
            if camera is not None:
                camera.release()
                print("Camera released")
            
            self.is_initialized = False
    
    def _update_preview_with_controller(self):
        """Fallback method using camera controller"""
        frame_count = 0
        print("Starting camera preview using controller...")
        
        while self.is_initialized:
            try:
                frame = self.camera_controller.get_preview_frame()
                
                if frame is not None:
                    frame_count += 1
                    
                    # Encode frame
                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    img_base64 = base64.b64encode(buffer.tobytes()).decode('utf-8')
                    
                    # Update UI
                    self.camera_preview.src_base64 = img_base64
                    self.page.update(self.camera_preview)
                    
                    if frame_count % 30 == 0:
                        print(f"Controller frame #{frame_count} displayed")
                else:
                    print("No frame from controller")
                    time.sleep(0.1)
                
                # Control frame rate
                time.sleep(0.04)
            except Exception as e:
                print(f"Controller preview error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(0.1)
    
    def capture_photo(self, e=None):
        """Capture a photo and add to thumbnails"""
        if not self.is_initialized or not hasattr(self, 'latest_frame'):
            print("Camera not initialized or no frame available")
            return
        
        # Flash effect
        self._flash_effect()
        
        try:
            # Use the latest frame directly
            if self.latest_frame is not None:
                # Create output directory if it doesn't exist
                import os
                output_dir = os.path.join(os.path.expanduser("~"), "SelfieBooth_Media")
                os.makedirs(output_dir, exist_ok=True)
                
                # Create filename with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(output_dir, f"photo_{timestamp}.jpg")
                
                # Save the photo
                cv2.imwrite(filepath, self.latest_frame)
                print(f"Photo saved to {filepath}")
                
                # Add thumbnail
                self._add_thumbnail(filepath, "photo")
            else:
                print("No frame available for capture")
        except Exception as e:
            print(f"Error capturing photo: {e}")
            import traceback
            traceback.print_exc()
    def toggle_recording(self, e=None):
        """Start or stop video recording using direct camera access"""
        import os, datetime  # Import needed modules at the method level
        
        if not self.is_initialized or not hasattr(self, 'latest_frame'):
            print("Camera not initialized or no frame available")
            return
        
        if not self.is_recording:
            try:
                # Create output directory if it doesn't exist
                output_dir = os.path.join(os.path.expanduser("~"), "SelfieBooth_Media")
                os.makedirs(output_dir, exist_ok=True)
                
                # Create filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                self.output_path = os.path.join(output_dir, f"video_{timestamp}.mp4")
                
                # Initialize video writer
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(
                    self.output_path,
                    fourcc,
                    30.0,  # FPS
                    (self.latest_frame.shape[1], self.latest_frame.shape[0])
                )
                
                if not self.video_writer.isOpened():
                    raise Exception("Failed to open video writer")
                
                print(f"Started recording video to {self.output_path}")
                self.is_recording = True
                self.recording_start_time = time.time()
                self.video_button.text = "Stop Recording"
                self.video_button.bgcolor = "#7f1d1d"
                self.capture_button.disabled = True
                
                # Start recording timer
                self.recording_seconds = 0
                self._start_recording_timer()
                
                # Auto-stop after 5 seconds for special modes
                if self.mode == "gif" or self.mode == "boomerang":
                    max_seconds = 3 if self.mode == "boomerang" else 5
                    threading.Timer(max_seconds, self.toggle_recording).start()
                
                self.status_text.value = "Recording started"
            except Exception as e:
                print(f"Error starting recording: {e}")
                import traceback
                traceback.print_exc()
                self.status_text.value = f"Failed to start recording: {str(e)}"
                self.status_text.color = "red"
        else:
            try:
                # Calculate duration
                duration = time.time() - self.recording_start_time
                
                # Stop recording
                if hasattr(self, 'video_writer') and self.video_writer is not None:
                    self.video_writer.release()
                    self.video_writer = None
                    print(f"Video recording stopped after {duration:.1f}s")
                    
                    # Reset UI
                    self.is_recording = False
                    self.video_button.text = "Start Recording"
                    self.video_button.bgcolor = "#e11d48"
                    self.capture_button.disabled = False
                    
                    # Add thumbnail
                    if hasattr(self, 'output_path') and os.path.exists(self.output_path):
                        self._add_thumbnail(self.output_path, "video")
                        self.status_text.value = f"Video recorded ({duration:.1f}s)"
                    else:
                        self.status_text.value = "Video saved but file not found"
                    
                    # Stop timer
                    self.recording_seconds = 0
                else:
                    self.status_text.value = "No video writer to stop"
            except Exception as e:
                print(f"Error stopping recording: {e}")
                import traceback
                traceback.print_exc()
                self.status_text.value = f"Failed to stop recording: {str(e)}"
                self.status_text.color = "red"
        
        self.update()
    
    def _start_recording_timer(self):
        """Update recording timer display"""
        if not self.is_recording:
            return
        
        self.recording_seconds += 1
        self.status_text.value = f"Recording: {self.recording_seconds}s"
        self.update()
        
        # Schedule next update
        if self.is_recording:
            threading.Timer(1.0, self._start_recording_timer).start()
    
    def _flash_effect(self):
        """Create a flash effect when taking photo"""
        # Create a white overlay
        flash = ft.Container(
            bgcolor=ft.Colors.with_opacity(0.7, "#ffffff"),
            width=640,
            height=480,
            border_radius=10,
        )
        
        # Add to preview container
        self.preview_container.content = ft.Stack([
            self.camera_preview,
            flash,
        ])
        self.update()
        
        # Remove flash after short delay
        def remove_flash():
            self.preview_container.content = self.camera_preview
            self.update()
        
        threading.Timer(0.1, remove_flash).start()
    
    def _add_thumbnail(self, filepath, media_type):
        """Add a thumbnail for captured media"""
        try:
            # Create thumbnail container
            thumbnail = ft.Container(
                content=ft.Image(
                    src=filepath,
                    width=120,
                    height=120,
                    fit=ft.ImageFit.COVER,
                    border_radius=5,
                ),
                width=120,
                height=120,
                border_radius=5,
                on_click=lambda e, path=filepath: self._preview_media(path),
                tooltip=f"{media_type.capitalize()}: {os.path.basename(filepath)}",
            )
            
            # Add to thumbnails row
            self.thumbnails_row.controls.insert(0, thumbnail)
            self.update()
        except Exception as e:
            print(f"Error adding thumbnail: {e}")
    
    def _preview_media(self, filepath):
        """Show a larger preview of the selected media"""
        # This would be implemented with more time
        pass
    
    def _create_placeholder_image(self):
        """Create a simple black placeholder image as base64 string"""
        try:
            import numpy as np
            import cv2
            import base64
                
            # Create a black image
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                
            # Add text to indicate it's loading
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(placeholder, "Initializing Camera...", (160, 240), font, 1, (255, 255, 255), 2)
                
            # Convert to base64 (no data URI prefix for Flet's src_base64)
            _, buffer = cv2.imencode('.jpg', placeholder)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            print(f"Error creating placeholder image: {e}")
            # Return a minimal valid 1x1 black JPEG as base64 if anything fails
            return "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9/KKKKAP/2Q=="
    
    def handle_back(self):
        """Handle back button click"""
        # Stop recording if active
        if self.is_recording:
            self.toggle_recording(None)
            
        # Go back to experience selection
        self.page.go(f"/experience/{self.event_id}")
