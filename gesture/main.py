import cv2 
import mediapipe as mp
import pickle 
import numpy as np
import os
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

print("Loading the model7..")
with open('gest-model.pkl', 'rb') as f:
    model = pickle.load(f)
    
gestlist = {}

with open('labelgesture.txt', 'r') as f:
    for line in f:
        clean_line = line.replace(',','').strip()
        if not clean_line:
          continue
        if ':' in clean_line:
            number_part, namepart = clean_line.split(':',1)

            gest_num = int(number_part.strip())
            gest_name = namepart.strip()

            gestlist[gest_num] = gest_name
print(f"Loaded {len(gestlist)} gestures: {gestlist}")


model_path = 'hand_landmarker.task'
base_options = python.BaseOptions(model_asset_path= model_path)
options = vision.HandLandmarkerOptions(base_options = base_options, num_hands = 1)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
print("Webcam Started")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.flip(image, 1)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    detectionres = detector.detect(mp_image)

    if detectionres.hand_landmarks:
        hand_landmarks = detectionres.hand_landmarks[0]

        for landmark in hand_landmarks:
            x = int(landmark.x * image.shape[1])
            y = int(landmark.y * image.shape[0])
            cv2.circle(image, (x,y), 5, (255, 0 , 0), -1)
        
        row = []
        for landmark in hand_landmarks:
            row.extend([landmark.x, landmark.y, landmark.z])
        
        input = np.array([row])

        pred =model.predict(input)
        pred_label_number = pred[0]

        gest_name = gestlist.get(pred_label_number, "Unknown")

        cv2.putText(image, f'Gesture: {gest_name}', (10,50), cv2.FONT_HERSHEY_PLAIN, 1.5, (255,0,0), 3)

    cv2.imshow("LiveShit", image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()