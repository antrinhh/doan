import cv2
import numpy as np

# red LAB range
lower_red = np.array([20, 140, 120])
upper_red = np.array([255, 230, 238])
# green LAB range
lower_green = np.array([0, 0, 126])
upper_green = np.array([255, 127, 255])
# blue LAB range
lower_blue = np.array([0, 0, 0])
upper_blue = np.array([132, 138, 109])


def DetectColor(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    scale = 1.2
    hsv[:, :, 1] = hsv[:, :, 1]*scale
    image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    roi = image[184:294, 247:343]
    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)

    mask_red = cv2.inRange(lab, lower_red, upper_red)
    mask_green = cv2.inRange(lab, lower_green, upper_green)
    mask_blue = cv2.inRange(lab, lower_blue, upper_blue)
    total_pixels = roi.shape[0]*roi.shape[1]
    percent_red = cv2.countNonZero(mask_red) / total_pixels
    percent_green = cv2.countNonZero(mask_green)/total_pixels
    percent_blue = cv2.countNonZero(mask_blue)/total_pixels
    cv2.imshow("roi", roi)
    cv2.imshow("green's mask", mask_green)
    cv2.imshow("blue's mask", mask_blue)
    cv2.imshow("red's mask", mask_red)
    if percent_red > 0.75:
        return "red", (0, 0, 255)
    elif percent_green > 0.75:
        return "green", (0, 255, 0)
    elif percent_blue > 0.6:
        return "blue", (255, 0, 0)
    else:
        return "unknown", (150, 150, 150)
