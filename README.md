# Driver-Drowsiness-Detection-System

Driver Drowsiness Detection System is a Python-based project that uses `OpenCV`, `dlib`, `imutils`, and `pygame` to detect driver fatigue in real-time using facial landmarks.

### Overview

This project contains a Python script that uses a webcam to monitor a driver's eye movement and determine whether they are drowsy or alert. If the driver is found to be drowsy, the system triggers an alarm to prevent potential accidents.

The project includes the following components:

1. `DriverDrowsy.py` – Main script that implements the drowsiness detection logic.
2. `shape_predictor_68_face_landmarks.dat` – Pre-trained model for facial landmark detection.

---

### 1. DriverDrowsy.py
- Captures live video stream using the system's webcam.
- Detects face using `dlib.get_frontal_face_detector()`.
- Uses 68 facial landmarks to monitor eye movement and calculate the Eye Aspect Ratio (EAR).
- If EAR drops below a defined threshold for a set number of consecutive frames, the system triggers an audible alarm using `pygame`.
- Displays the real-time EAR value and status ("Drowsy" or "Alert") on the screen.

---

### 2. shape_predictor_68_face_landmarks.dat
- A pre-trained model file used by dlib to detect facial landmarks like eyes, nose, lips, etc.
- Required for accurate EAR calculation.
- Must be placed in the project directory.

---

### How It Works
- The Eye Aspect Ratio (EAR) is computed using vertical and horizontal distances between eye landmarks.
- If the EAR falls below a certain threshold (e.g., 0.25) and remains below it for a fixed number of frames (e.g., 48), the system considers the driver drowsy.
- A buzzer sound is played to alert the driver.

---

### Pre-Requisites

Ensure that you have the following Python packages installed:

- `opencv-python`: `pip install opencv-python`
- `dlib`: `pip install dlib`
- `imutils`: `pip install imutils`
- `pygame`: `pip install pygame`

You must also download and extract:
- `shape_predictor_68_face_landmarks.dat` from [this link](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)

---

### Steps to Run the Project

1. Download and extract the project folder.
2. Download and place `shape_predictor_68_face_landmarks.dat` inside the project folder.
3. Ensure your webcam is connected and accessible.
4. Run the script using the command:

### Features

- Real-time face and eye tracking
- Eye Aspect Ratio (EAR) based detection
- Audio alarm when drowsiness is detected
- Simple and efficient logic for on-device computation

---

## 🛠️ Tech Stack

- Python
- OpenCV
- mediapipe 
- imutils
- pygame

---

## 📁 Folder Structure

DriverDrowsinessDetectionSystem/
├── DriverDrowsy.py
├── shape_predictor_68_face_landmarks.dat
└── README.md

yaml
Copy
Edit

---

## 🚀 How It Works

1. Webcam captures live video.
2. dlib detects facial landmarks.
3. EAR (Eye Aspect Ratio) is calculated:
   - If EAR < threshold (e.g., 0.25) for consecutive frames (e.g., 48 frames), it's considered drowsiness.
4. Pygame triggers a buzzer sound to wake the driver.

---

## 🧠 Eye Aspect Ratio (EAR)

EAR is calculated as:

EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)

yaml
Copy
Edit

Where `p1...p6` are specific eye landmarks. A lower EAR indicates closed eyes.

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/DriverDrowsinessDetectionSystem.git
cd DriverDrowsinessDetectionSystem
