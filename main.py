import cv2
from detect_color_in_box import DetectColor
from connector import Connector

connector = Connector()
last_color = None
cap = cv2.VideoCapture(2)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    color_name, color_scalar = DetectColor(frame)
    if color_name != last_color and (color_name == "red" or color_name == "green" or color_name == "blue"):
        connector.SendCommand(color_name)
        last_color = color_name
    cv2.putText(frame, f"Color: {color_name}", (10, 450),
                cv2.FONT_HERSHEY_COMPLEX, 0.5, color_scalar, 2)
    cv2.imshow("video", frame)
    if cv2.waitKey(16) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
