from torch.xpu import device
from ultralytics import YOLO
import cv2
import mediapipe as mp


model = YOLO("yolo11n.pt")


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=4,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)


cap = cv2.VideoCapture(r"D:\PyCharm\YOLO_11\poses\nabhonil.mp4")  # Replace with video path if needed

# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0


fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec
out = cv2.VideoWriter("output_yolo_hands.mp4", fourcc, fps, (width, height))

#  display window
cv2.namedWindow("YOLO + Hands", cv2.WINDOW_NORMAL)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # No mirroring y
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Person Detection
    results = model.predict(frame_rgb, classes=[0], stream=False, verbose=False,device=0)

    if results:
        result = results[0]
        boxes = result.boxes

        if boxes is not None:
            for box, conf in zip(boxes.xyxy, boxes.conf):
                if conf > 0.5:
                    x1, y1, x2, y2 = map(int, box)
                    # Draw person box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f'Person: {conf:.2f}', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    #  Mediapipe Hand Detection
    hand_results = hands.process(frame_rgb)

    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Optional: Draw circle on index finger tip
            index_tip = hand_landmarks.landmark[8]
            h, w, _ = frame.shape
            cx, cy = int(index_tip.x * w), int(index_tip.y * h)
            cv2.circle(frame, (cx, cy), 8, (255, 0, 0), -1)
            cv2.putText(frame, "Index Tip", (cx + 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)


    out.write(frame)


    cv2.imshow("YOLO + Hands", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
out.release()
cv2.destroyAllWindows()
