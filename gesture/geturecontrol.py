import cv2
import mediapipe as mp
import os
import urllib.request
import pyautogui as ag
from collections import deque, Counter
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- AUTO-DOWNLOAD MODEL ---
model_path = 'gesture_recognizer.task'
if not os.path.exists(model_path):
    print("Downloading model...")
    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task", model_path)

# 1. Setup Tasks API
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=1)
recognizer = vision.GestureRecognizer.create_from_options(options)

# --- THE VOTING SETTINGS ---
MIN_CONFIDENCE = 0.50          # Lowered to 50% to be a bit more forgiving
BUFFER_SIZE = 10               # Keep track of the last 10 frames
VOTES_NEEDED = 6               # The gesture needs 6 out of 10 votes to win

gesture_buffer = deque(maxlen=BUFFER_SIZE)
current_stable_gesture = "None"

# 2. Open Webcam
cap = cv2.VideoCapture(0)
print("Webcam started! Look for the blue dots.")

while cap.isOpened():
    success, image = cap.read()
    if not success: continue

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    
    recognition_result = recognizer.recognize(mp_image)

    # --- DRAW THE SKELETON FIRST ---
    # This proves the AI actually sees your hand!
    if recognition_result.hand_landmarks:
        hand_landmarks = recognition_result.hand_landmarks[0]
        for landmark in hand_landmarks:
            x = int(landmark.x * image.shape[1])
            y = int(landmark.y * image.shape[0])
            cv2.circle(image, (x, y), 5, (255, 0, 0), -1)

    # --- THE VOTING LOGIC ---
    frame_gesture = "None"

    if recognition_result.gestures:
        top_gesture = recognition_result.gestures[0][0]
        if top_gesture.score > MIN_CONFIDENCE:
            frame_gesture = top_gesture.category_name

    # Add the current frame's guess to the ballot box
    gesture_buffer.append(frame_gesture)

    # Once we have 10 frames in the box, tally the votes!
    if len(gesture_buffer) == BUFFER_SIZE:
        # Get the most common gesture and how many votes it got
        most_common = Counter(gesture_buffer).most_common(1)[0]
        best_gesture = most_common[0]
        vote_count = most_common[1]
        
        # If the winner got at least 6 votes, it becomes our official stable gesture
        if vote_count >= VOTES_NEEDED:
            current_stable_gesture = best_gesture
        if "Thumb_Up" in best_gesture:
            ag.press("Enter")

    # Display the winning gesture on screen
    if current_stable_gesture != "None":
        cv2.putText(image, f"Gesture: {current_stable_gesture}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow('Voting Gesture AI', image)
    
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()