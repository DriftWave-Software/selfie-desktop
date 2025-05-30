#!/usr/bin/env python3
"""
Camera diagnostic tool for macOS.
This script checks camera availability and access permissions.
"""
import cv2
import sys
import platform
import subprocess
import time
import os

def print_system_info():
    """Print system information."""
    print(f"Python version: {sys.version}")
    print(f"OpenCV version: {cv2.__version__}")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Platform: {platform.platform()}")
    print()

def check_camera_permission():
    """Check if camera permission has been granted on macOS."""
    if platform.system() != "Darwin":
        print("Not running on macOS, skipping permission check.")
        return
    
    # Try to use tccutil to check camera permissions (requires admin)
    try:
        print("Checking camera permissions...")
        # This might not work without sudo privileges
        result = subprocess.run(
            ["tccutil", "status", "Camera"], 
            capture_output=True, 
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"Could not check permissions programmatically: {e}")
        print("Please check manually in System Preferences > Security & Privacy > Privacy > Camera")

def list_available_cameras():
    """List all available camera devices."""
    print("Checking available cameras...")
    available_cameras = []
    
    # Try up to 10 camera indices
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                resolution = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                             int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                fps = cap.get(cv2.CAP_PROP_FPS)
                available_cameras.append((i, resolution, fps))
                print(f"Camera #{i} is available - Resolution: {resolution}, FPS: {fps}")
            else:
                print(f"Camera #{i} is connected but couldn't read frame")
            cap.release()
        else:
            print(f"Camera #{i} is not available")
    
    print(f"Found {len(available_cameras)} working cameras")
    return available_cameras

def test_specific_camera(camera_id=0, duration=5):
    """Test a specific camera by capturing frames for a set duration."""
    print(f"\nTesting camera #{camera_id} for {duration} seconds...")
    
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"Could not open camera #{camera_id}")
        return False
    
    print(f"Camera #{camera_id} opened successfully")
    print(f"Width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
    print(f"Height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if ret:
            frame_count += 1
            if frame_count % 10 == 0:
                print(f"Captured {frame_count} frames")
        else:
            print("Failed to capture frame")
            break
        time.sleep(0.01)
    
    cap.release()
    fps = frame_count / duration
    print(f"Camera test completed. Captured {frame_count} frames in {duration} seconds ({fps:.2f} FPS)")
    return True

def main():
    """Main diagnostic function."""
    print("===== Camera Diagnostic Tool =====")
    print_system_info()
    
    print("\n===== Camera Permissions =====")
    check_camera_permission()
    
    print("\n===== Camera Availability =====")
    available_cameras = list_available_cameras()
    
    if available_cameras:
        for camera_id, _, _ in available_cameras:
            test_specific_camera(camera_id, duration=3)
    else:
        print("\nNo working cameras found. Please check your camera connections and permissions.")
        print("For macOS: System Preferences > Security & Privacy > Privacy > Camera")
        
    print("\n===== Diagnostic Complete =====")

if __name__ == "__main__":
    main()
