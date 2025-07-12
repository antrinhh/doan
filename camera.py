import cv2 as cv

def find_first_camera(max_test=10):
    for i in range(max_test):
        cap = cv.VideoCapture(i)
        if cap is not None and cap.isOpened():
            return cap
        cap.release()
    raise RuntimeError("No camera found")

cap = find_first_camera()

while True:
    ret, frame = cap.read()
    

    cv.imshow("frame", frame)

    if cv.waitKey(1) == ord('q'):
        break

cv.destroyAllWindows()
cap.release()
