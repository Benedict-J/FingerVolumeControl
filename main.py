import cv2
import mediapipe as mp
import numpy as np
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

vol_range = volume.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

volume.SetMute(0, None)
volume.SetMasterVolumeLevel(0, None)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

camera = cv2.VideoCapture(0)

max_distance = 100
min_distance = 0

def main():
    hands = mp_hands.Hands()

    while True:
        _, frame = camera.read()
        height, width, _ = frame.shape

        results = hands.process(frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

                # Thumb coordinate
                x1 = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * width
                y1 = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * height
                # Index finger coordinate
                x2 = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * width
                y2 = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * height

                # Draw line between Thumb and Index Finger
                cv2.line(frame,
                         (int(x1), int(y1)),
                         (int(x2), int(y2)), (0, 255, 0), thickness=2)

                distance = math.sqrt(pow(int(x2) - int(x1), 2) + pow(int(y2) - int(y1), 2))

                desired_vol_db = np.interp(distance, [0, 100], [min_vol, max_vol])
                volume.SetMasterVolumeLevel(desired_vol_db, None)

                current_vol = volume.GetMasterVolumeLevelScalar() * 100

                # Show a text message
                if current_vol <= 3:
                    cv2.putText(frame, "DIAM!!!", (100, 100), 3, 3, (0,0,255), 2)



        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            camera.release()
            cv2.destroyAllWindows()


if __name__ == '__main__':
    main()