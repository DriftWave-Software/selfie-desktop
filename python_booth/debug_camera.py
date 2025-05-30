import flet as ft
import cv2
import threading
import base64
import time

class SimpleCameraApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Camera Debug"
        self.page.padding = 10
        
        # Camera state
        self.camera = None
        self.camera_id = 0
        self.is_running = False
        self.frame_lock = threading.Lock()
        self.latest_frame = None
        
        # Create UI elements
        self.status_text = ft.Text("Camera status: Not started", color="orange")
        self.camera_view = ft.Image(
            width=640,
            height=480,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10,
        )
        
        self.start_button = ft.ElevatedButton(
            "Start Camera",
            on_click=self.start_camera,
            style=ft.ButtonStyle(
                color="white",
                bgcolor="green",
            )
        )
        
        self.stop_button = ft.ElevatedButton(
            "Stop Camera",
            on_click=self.stop_camera,
            disabled=True,
            style=ft.ButtonStyle(
                color="white",
                bgcolor="red",
            )
        )
        
        # Layout
        self.page.add(
            ft.Column([
                ft.Text("Camera Debug Tool", size=24, weight=ft.FontWeight.BOLD),
                self.status_text,
                ft.Container(
                    content=self.camera_view,
                    border=ft.border.all(2, "grey"),
                    border_radius=10,
                    padding=5,
                    margin=ft.margin.symmetric(vertical=10)
                ),
                ft.Row([
                    self.start_button,
                    self.stop_button
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            ])
        )
    
    def start_camera(self, e=None):
        """Start the camera capture thread"""
        self.status_text.value = "Starting camera..."
        self.page.update(self.status_text)
        
        # Create a separate thread for camera initialization
        threading.Thread(target=self._initialize_camera, daemon=True).start()
    
    def _initialize_camera(self):
        """Initialize the camera in a background thread"""
        try:
            # Initialize the camera
            self.camera = cv2.VideoCapture(self.camera_id)
            if not self.camera.isOpened():
                self.status_text.value = f"Error: Could not open camera {self.camera_id}"
                self.status_text.color = "red"
                self.page.update(self.status_text)
                return
            
            # Set resolution
            width = 640
            height = 480
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Log actual camera properties
            actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            # Update status
            self.status_text.value = f"Camera ready: {actual_width}x{actual_height} @ {fps}fps"
            self.status_text.color = "green"
            self.page.update(self.status_text)
            
            # Update buttons
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.page.update(self.start_button)
            self.page.update(self.stop_button)
            
            # Start capture thread
            self.is_running = True
            threading.Thread(target=self._capture_frames, daemon=True).start()
            
        except Exception as e:
            self.status_text.value = f"Camera error: {str(e)}"
            self.status_text.color = "red"
            self.page.update(self.status_text)
    
    def _capture_frames(self):
        """Continuously capture and display frames"""
        frame_count = 0
        update_interval = 0.033  # ~30 FPS
        
        while self.is_running:
            try:
                if not self.camera.isOpened():
                    self.status_text.value = "Error: Camera disconnected"
                    self.status_text.color = "red"
                    self.page.update(self.status_text)
                    break
                
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    print("Warning: Could not read frame")
                    time.sleep(0.1)
                    continue
                
                frame_count += 1
                
                # Convert frame to base64 for display (every frame)
                _, buffer = cv2.imencode('.jpg', frame)
                img_bytes = buffer.tobytes()
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                
                # Update the UI with the frame
                self.camera_view.src_base64 = img_base64
                self.page.update(self.camera_view)
                
                # Log progress occasionally
                if frame_count % 30 == 0:
                    print(f"Processed {frame_count} frames")
                
                # Control frame rate
                time.sleep(update_interval)
                
            except Exception as e:
                print(f"Frame capture error: {e}")
                time.sleep(0.1)
    
    def stop_camera(self, e=None):
        """Stop the camera and release resources"""
        self.is_running = False
        
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        
        self.status_text.value = "Camera stopped"
        self.status_text.color = "orange"
        
        self.start_button.disabled = False
        self.stop_button.disabled = True
        
        self.page.update(self.status_text)
        self.page.update(self.start_button)
        self.page.update(self.stop_button)

def main(page: ft.Page):
    app = SimpleCameraApp(page)

if __name__ == '__main__':
    ft.app(target=main)
