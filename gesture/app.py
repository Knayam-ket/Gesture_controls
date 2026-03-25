import cv2
import mediapipe as mp
import urllib.request
import os
import csv
from mediapipe.tasks import python
from mediapipe.tasks.python import vision



model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Downloading the model file from Google. Please wait...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print("Download complete!")

currentgesturelabel = 7
csv_file = 'gesture_dataset.csv'

if not os.path.exists(csv_file):
    with open(csv_file, mode = 'w', newline='') as f:
        writer = csv.writer(f)
        headers = []
        for i in range(21):
            headers.extend([f'x{i}', f'y{i}', f'z{i}'])
        headers.append('label')
        writer.writerow(headers)

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)

print("Starting webcam...")
cap = cv2.VideoCapture(0)
print("Webcam Started!")


while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue
    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

   
    detection_result = detector.detect(mp_image)

    if detection_result.hand_landmarks:
        hand_landmarks = detection_result.hand_landmarks[0]
        
        for landmark in hand_landmarks:
            x = int(landmark.x * image.shape[1])
            y = int(landmark.y * image.shape[0])
                
            cv2.circle(image, (x, y), 5, (0, 255 , 0), -1)


        key = cv2.waitKey(5) & 0xFF
        if key == ord('s'):
           
            row = []
            for landmark in hand_landmarks:
                row.extend([landmark.x, landmark.y, landmark.z])
            
            row.append(currentgesturelabel)
            
            # Append to CSV
            with open(csv_file, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            print(f"Saved 1 frame for label {currentgesturelabel}!")
    cv2.imshow('Hand Tracking', image)
    
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()