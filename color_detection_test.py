import cv2
import numpy as np

# img = cv2.imread("IMG_2978.jpg")
# img = cv2.resize(img, (640, 480))
cap = cv2.VideoCapture(0)
while True:
    ret, img = cap.read()

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    mask = cv2.inRange(lab, (20, 140, 120), (255, 230, 238))
    # mask = cv2.GaussianBlur(mask, (5, 5), 1.5)

    # mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    # erode = cv2.erode(mask, kernel_erode)
    # dialate = cv2.dilate(erode, kernel_dialate)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 1000:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img, (x, y), (x + w + 5, y + h + 5),
                          (0, 255, 0), 2)
    # cv2.imshow("lab", lab)
    cv2.imshow("mask", mask)
    # cv2.imshow("erode", erode)
    # cv2.imshow("dialate", dialate)
    # cv2.imshow("open", open)
    cv2.imshow("image", img)
    if cv2.waitKey(16) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
