import cv2

tracker = cv2.TrackerCSRT_create()

cap = cv2.VideoCapture("randomball.avi")
ret, frame = cap.read()
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 50))
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
if contours:
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    tracker.init(frame, (x, y, w, h))

fps = None
while True:
    ret, frame = cap.read()

    success, box = tracker.update(frame)

    if success:
        x, y, w, h = [int(v) for v in box]
        cv2.rectangle(frame, (x - 3, y-3),
                      (x + w, y + h), (0, 0, 255), 2)
    cv2.imshow("Tracking", frame)

    if cv2.waitKey(16) == ord('q'):
        break

fps.stop()
cap.release()
cv2.destroyAllWindows()
