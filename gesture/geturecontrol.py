import cv2
import mediapipe as mp
import urllib.request
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- AUTO-DOWNLOAD THE PRE-TRAINED GESTURE MODEL ---
model_path = 'gesture_recognizer.task'
if not os.path.exists(model_path):
    print("Downloading Google's Pre-trained Gesture Model...")
    url = "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"
    urllib.request.urlretrieve(url, model_path)
    print("Download complete!")

# 1. Setup the Tasks API for Gesture Recognition
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=1)
recognizer = vision.GestureRecognizer.create_from_options(options)

# 2. Open the webcam
cap = cv2.VideoCapture(0)
print("Webcam started! Try a Thumbs Up or Peace Sign.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    # Flip the camera like a mirror
    image = cv2.flip(image, 1)

    # Convert to MediaPipe Image format
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    
    # 3. Predict the gesture using the pre-trained model!
    recognition_result = recognizer.recognize(mp_image)

    # 4. If a gesture is detected...
    if recognition_result.gestures:
        # Grab the top predicted gesture
        top_gesture = recognition_result.gestures[0][0]
        gesture_name = top_gesture.category_name
        confidence = top_gesture.score

        # Ignore "None" (which just means a hand is present but doing nothing specific)
        if gesture_name != "None":
            # Display the Gesture and the Confidence Score (%)
            text = f"{gesture_name} ({confidence*100:.0f}%)"
            cv2.putText(image, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

    # 5. (Optional) We can still draw the hand landmarks!
    if recognition_result.hand_landmarks:
        hand_landmarks = recognition_result.hand_landmarks[0]
        for landmark in hand_landmarks:
            x = int(landmark.x * image.shape[1])
            y = int(landmark.y * image.shape[0])
            cv2.circle(image, (x, y), 5, (255, 0, 0), -1)

    # Show the video feed
    cv2.imshow('Pre-Trained Gesture AI', image)
    
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()