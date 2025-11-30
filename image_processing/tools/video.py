import cv2
import os
import subprocess

def extractFrames(video_path, output_dir="frames"):
    os.makedirs(str(output_dir), exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("Could not open video.")

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        filename = os.path.join(output_dir, f"frame_{frame_idx:06d}.png")
        cv2.imwrite(filename, frame)
        frame_idx += 1

    cap.release()
    print(f"Saved {frame_idx} frames to {output_dir}")