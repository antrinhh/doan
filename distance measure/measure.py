import cv2
import numpy as np

measured_distance = 19 #khoảng cách mẫu để tính focal_length
real_width = 2.5 #kích thước thật của vật


def ObjectData(img):
    w = 0
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lower = np.array([20, 149, 120])
    upper = np.array([255, 230, 238])
    mask = cv2.inRange(lab, lower, upper)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 1000:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    return w


def FocalLength(img_w):
    global measured_distance, real_width
    focal = (img_w*measured_distance)/real_width
    return focal


def Distance_finder(Focal_Length, img_w):
    distance = (real_width * Focal_Length)/img_w
    return distance


def WriteDistance(img, dis):
    text = f"{round(dis,2)}cm"
    cv2.putText(img, text, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


def main():
    focal_length = 851.2
    # img = cv2.imread("data/test_image4.jpg")
    cap = cv2.VideoCapture(2)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("cant open camera")
            break
        image_width = ObjectData(frame)
        if image_width:
            # focal_length = FocalLength(image_width)

            distance = Distance_finder(focal_length, image_width)
            WriteDistance(frame, distance)
            # cv2.putText(frame, f"{focal_length}", (50, 50),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("image", frame)
        if cv2.waitKey(16) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
