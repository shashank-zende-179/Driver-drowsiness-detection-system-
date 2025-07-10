import cv2
import numpy as np
import mediapipe as mp
import pygame
import threading
import os
import logging
import atexit
import time  # NEW
from typing import Tuple, List

# === Configuration ===
CONFIG = {
    "EAR_THRESHOLD_DROWSY": 0.25,
    "EAR_THRESHOLD_CLOSED": 0.21,
    "INACTIVITY_FRAMES": 6,
    "HEAD_DOWN_RATIO": 0.65,
    "MOTION_THRESHOLD": 10,
    "FRAME_SKIP": 2,
    "ALARM_FILE": "DriverDrowsinessDetectionSystem/alarm.wav"
}

# === Logging Setup ===
logging.basicConfig(
    filename='drowsiness.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# === Alarm Setup ===
pygame.mixer.init()
alarm_playing = False
alarm_lock = threading.Lock()

def play_alarm():
    global alarm_playing
    with alarm_lock:
        if not alarm_playing:
            try:
                pygame.mixer.music.load(CONFIG["ALARM_FILE"])
                pygame.mixer.music.play(-1)
                alarm_playing = True
                logging.info("Alarm started")
            except Exception as e:
                logging.error(f"Failed to play alarm: {str(e)}")

def stop_alarm():
    global alarm_playing
    with alarm_lock:
        if alarm_playing:
            pygame.mixer.music.stop()
            alarm_playing = False
            logging.info("Alarm stopped")

# === Utility Functions ===
def compute(ptA: Tuple[int, int], ptB: Tuple[int, int]) -> float:
    return np.linalg.norm(np.array(ptA) - np.array(ptB))

def blinked(eye: List[Tuple[int, int]]) -> int:
    up = compute(eye[1], eye[5]) + compute(eye[2], eye[4])
    down = compute(eye[0], eye[3])
    ratio = up / (2.0 * down)
    
    if ratio > CONFIG["EAR_THRESHOLD_DROWSY"]:
        return 2  # open
    elif CONFIG["EAR_THRESHOLD_CLOSED"] <= ratio <= CONFIG["EAR_THRESHOLD_DROWSY"]:
        return 1  # drowsy
    return 0  # closed

# === MediaPipe Setup ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

# === Webcam Initialization ===
try:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam")
except Exception as e:
    logging.critical(f"Camera initialization failed: {str(e)}")
    exit(1)

# === Drowsiness Tracking ===
sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)
last_nose_pos = None
frame_counter = 0
head_down_start_time = None  # NEW

# === Cleanup Handler ===
def cleanup():
    stop_alarm()
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    logging.info("Application exited cleanly")

atexit.register(cleanup)

# === Main Loop ===
while True:
    ret, frame = cap.read()
    if not ret:
        logging.warning("Failed to capture frame")
        continue

    frame_counter += 1
    if CONFIG["FRAME_SKIP"] > 1 and frame_counter % CONFIG["FRAME_SKIP"] != 0:
        continue

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    
    face_frame = frame.copy()
    left_ear_ratio = right_ear_ratio = 0.0
    head_down = False  # RESET EACH FRAME

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            h, w = frame.shape[:2]
            lm = landmarks.landmark

            left_eye = [(int(lm[i].x * w), int(lm[i].y * h)) for i in [33, 160, 158, 133, 153, 144]]
            right_eye = [(int(lm[i].x * w), int(lm[i].y * h)) for i in [362, 385, 387, 263, 373, 380]]
            nose_point = (int(lm[1].x * w), int(lm[1].y * h))
            

            # EAR Calculation
            left_ear_ratio = (compute(left_eye[1], left_eye[5]) + compute(left_eye[2], left_eye[4])) / (2.0 * compute(left_eye[0], left_eye[3]))
            right_ear_ratio = (compute(right_eye[1], right_eye[5]) + compute(right_eye[2], right_eye[4])) / (2.0 * compute(right_eye[0], right_eye[3]))

            # === Head Down Detection with Delay ===
            if nose_point[1] > frame.shape[0] * CONFIG["HEAD_DOWN_RATIO"]:
                if head_down_start_time is None:
                    head_down_start_time = time.time()
                else:
                    if time.time() - head_down_start_time >= 3:
                        head_down = True
                        cv2.putText(frame, "Head Down Detected!", (10, 130),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)
            else:
                head_down_start_time = None  # Reset if head comes up

            # Blink detection
            left_blink = blinked(left_eye)
            right_blink = blinked(right_eye)

            if left_blink == 0 or right_blink == 0:
                sleep += 1
                drowsy = active = 0
                if sleep > CONFIG["INACTIVITY_FRAMES"]:
                    status = "SLEEPING !!!"
                    color = (255, 0, 0)
            elif left_blink == 1 or right_blink == 1:
                sleep = active = 0
                drowsy += 1
                if drowsy > CONFIG["INACTIVITY_FRAMES"]:
                    status = "Drowsy !"
                    color = (0, 0, 255)
            else:
                drowsy = sleep = 0
                active += 1
                if active > CONFIG["INACTIVITY_FRAMES"]:
                    status = "Active :)"
                    color = (0, 255, 0)

            cv2.putText(frame, status, (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            
            # Display EAR values
            cv2.putText(frame, f"Left EAR: {left_ear_ratio:.2f}", (10, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"Right EAR: {right_ear_ratio:.2f}", (10, 190), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            # === Alarm Logic ===
            drowsy_condition = status in ["SLEEPING !!!", "Drowsy !"]
            head_down_condition = head_down and (left_blink != 2 or right_blink != 2)

            if drowsy_condition or head_down_condition:
                play_alarm()
            else:
                stop_alarm()

    # Display instructions
    cv2.putText(frame, "Press 'q' to Exit", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    cv2.imshow("Drowsiness Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cleanup()
