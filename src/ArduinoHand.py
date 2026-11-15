"""Control five piano-key servos from MediaPipe hand landmarks."""

import argparse
import math

import cv2
import mediapipe as mp
import numpy as np
import pyfirmata2


SERVO_PINS = (4, 5, 6, 7, 8)
FINGER_LANDMARK_PAIRS = ((4, 1), (8, 5), (12, 9), (16, 13), (20, 17))
DISTANCE_RANGES = ((50, 220), (20, 150), (20, 150), (20, 150), (20, 150))
SERVO_RANGE = (0, 150)


def camera_source(value: str):
    """Interpret an integer as a webcam index; otherwise retain it as a URL/path."""
    try:
        return int(value)
    except ValueError:
        return value


def parse_args():
    parser = argparse.ArgumentParser(
        description="Map five finger distances to five Arduino-controlled servos."
    )
    parser.add_argument(
        "--camera",
        type=camera_source,
        default=0,
        help="Webcam index (default: 0), IP stream URL, or video path.",
    )
    parser.add_argument(
        "--port",
        default=pyfirmata2.Arduino.AUTODETECT,
        help="Arduino serial port (default: PyFirmata2 autodetection).",
    )
    parser.add_argument("--width", type=int, default=640, help="Requested frame width.")
    parser.add_argument("--height", type=int, default=480, help="Requested frame height.")
    return parser.parse_args()


def landmark_pixels(hand_landmarks, image_shape):
    height, width = image_shape[:2]
    return [
        (int(landmark.x * width), int(landmark.y * height))
        for landmark in hand_landmarks.landmark
    ]


def servo_angles(points):
    """Preserve the original continuous distance-to-angle mapping."""
    angles = []
    for (tip, base), distance_range in zip(
        FINGER_LANDMARK_PAIRS, DISTANCE_RANGES
    ):
        distance = math.hypot(
            points[tip][0] - points[base][0],
            points[tip][1] - points[base][1],
        )
        mapped_position = round(np.interp(distance, distance_range, SERVO_RANGE))
        angles.append(SERVO_RANGE[1] - mapped_position)
    return angles


def run(args):
    board = pyfirmata2.Arduino(args.port)
    servos = [board.get_pin(f"d:{pin}:s") for pin in SERVO_PINS]
    camera = cv2.VideoCapture(args.camera)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    if not camera.isOpened():
        board.exit()
        raise RuntimeError(f"Could not open camera source: {args.camera!r}")

    drawing = mp.solutions.drawing_utils
    drawing_styles = mp.solutions.drawing_styles
    hands_module = mp.solutions.hands

    try:
        with hands_module.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as hands:
            while camera.isOpened():
                success, image = camera.read()
                if not success:
                    print("Camera frame could not be read; stopping.")
                    break

                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_image)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        drawing.draw_landmarks(
                            image,
                            hand_landmarks,
                            hands_module.HAND_CONNECTIONS,
                            drawing_styles.get_default_hand_landmarks_style(),
                            drawing_styles.get_default_hand_connections_style(),
                        )

                    # Preserve original behavior: control from the first detected hand.
                    points = landmark_pixels(results.multi_hand_landmarks[0], image.shape)
                    for landmark_index in (0, 4, 8, 12, 16, 20):
                        cv2.circle(image, points[landmark_index], 15, (255, 255, 255))

                    angles = servo_angles(points)
                    print("Servo angles:", " ".join(map(str, angles)))
                    for servo, angle in zip(servos, angles):
                        servo.write(angle)

                cv2.imshow("handDetector", image)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        board.exit()


if __name__ == "__main__":
    run(parse_args())
