#!/usr/bin/env python3
import cv2
import time
import numpy as np

def test_camera():
    print("Starting camera test...")
    
    # Try different camera IDs
    for camera_id in range(3):  # Try camera IDs 0, 1, 2
        print(f"\nTesting camera ID: {camera_id}")
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"Camera ID {camera_id} could not be opened")
            continue
            
        print(f"Camera ID {camera_id} opened successfully!")
        
        # Get camera properties
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Camera properties: {width}x{height} @ {fps}fps")
        
        # Try to capture 10 frames
        frame_count = 0
        success_count = 0
        
        start_time = time.time()
        while frame_count < 10:
            ret, frame = cap.read()
            frame_count += 1
            
            if ret:
                success_count += 1
                print(f"Frame {frame_count} captured successfully. Shape: {frame.shape}")
            else:
                print(f"Frame {frame_count} capture failed")
            
            time.sleep(0.1)  # Short delay between frames
        
        end_time = time.time()
        
        print(f"Capture test completed for camera ID {camera_id}")
        print(f"Frames captured: {success_count}/{frame_count}")
        print(f"Time elapsed: {end_time - start_time:.2f} seconds")
        
        # Release this camera before trying the next one
        cap.release()
    
    print("\nCamera test completed!")

if __name__ == "__main__":
    test_camera()
