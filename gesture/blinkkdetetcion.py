import cv2
import mediapipe as mp
import urllib.request
import os
import math
import pyautogui
import pygetwindow as gw
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- AUTO-DOWNLOAD FACE MODEL ---
model_path = 'face_landmarker.task'
if not os.path.exists(model_path):
    print("Downloading Face model...")
    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task", model_path)

# --- EAR CALCULATION FUNCTION ---
def calculate_ear(eye_points):
    # Calculate vertical distances
    v1 = math.dist(eye_points[1], eye_points[5])
    v2 = math.dist(eye_points[2], eye_points[4])
    # Calculate horizontal distance
    h1 = math.dist(eye_points[0], eye_points[3])
    
    # EAR Formula
    ear = (v1 + v2) / (2.0 * h1)
    return ear

# 1. Setup Tasks API for Faces
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)
detector = vision.FaceLandmarker.create_from_options(options)

# 2. Open Webcam
cap = cv2.VideoCapture(0)
blink_count = 0
is_blinking = False

print("Webcam Started! Start blinking.")

while cap.isOpened():
    success, image = cap.read()
    if not success: continue

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    
    detection_result = detector.detect(mp_image)

    if detection_result.face_landmarks:
        face_landmarks = detection_result.face_landmarks[0]
        
        # Extract pixel coordinates for the 6 points of the Right Eye
        # MediaPipe standard indices for the Right Eye: 33, 160, 158, 133, 153, 144
        h, w, _ = image.shape
        right_eye_indices = [33, 160, 158, 133, 153, 144]
        right_eye_points = [(int(face_landmarks[i].x * w), int(face_landmarks[i].y * h)) for i in right_eye_indices]
        
        # Draw the points so you can see them
        for point in right_eye_points:
            cv2.circle(image, point, 2, (0, 255, 255), -1)

        # Calculate the EAR
        ear = calculate_ear(right_eye_points)
        
       
        if ear < 0.12:
            if not is_blinking:
                blink_count += 1
                is_blinking = True
                activewin = gw.getActiveWindowTitle()
                if "Instagram" in activewin or "instagram" in activewin:
                    pyautogui.press("down")
                    cv2.putText(image, "Down Triggered", (100,100), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0,0,255), 3)

                
                cv2.putText(image, "BLINK DETECTED!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        else:
            is_blinking = False

        # Display EAR and Count
        cv2.putText(image, f'EAR: {ear:.2f}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(image, f'Blinks: {blink_count}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Blink Detector", image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()