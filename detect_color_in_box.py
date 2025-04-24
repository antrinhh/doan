import cv2
import numpy as np

# red LAB range
lower_red = np.array([20, 140, 120])
upper_red = np.array([255, 230, 238])
# green LAB range
lower_green = np.array([0, 0, 126])
upper_green = np.array([255, 255, 255])
# blue LAB range
lower_blue = np.array([0, 0, 96])
upper_blue = np.array([255, 255, 255])
color = (200, 200, 200)
detected = False
frame_count = 0
label = "Detecting.."
cap = cv2.VideoCapture(2)
while True:
    ret, frame = cap.read()
    frame_count += 1
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    scale = 1.2
    hsv[:, :, 1] = hsv[:, :, 1]*scale
    # hsv[:, :, 2] = hsv[:, :, 2]*1.2
    image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    roi = image[162:378, 152:357]

    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    if not detected and frame_count > 10:

        mask_red = cv2.inRange(lab, lower_red, upper_red)
        mask_green = cv2.inRange(lab, lower_green, upper_green)
        mask_blue = cv2.inRange(lab, lower_blue, upper_blue)

        # do range mau cua cai blue no khong on
        mask_blue = cv2.bitwise_not(mask_blue)

        total_pixels = roi.shape[0]*roi.shape[1]
        percent_red = cv2.countNonZero(mask_red) / total_pixels
        percent_green = cv2.countNonZero(mask_green)/total_pixels
        percent_blue = cv2.countNonZero(mask_blue)/total_pixels

    # for i in range(roi.shape[0]):     # tức là chiều cao: 386 - 174 = 212
    #     for j in range(roi.shape[1]):  # tức là chiều rộng: 330 - 165 = 165
    #         if (lower[0] < lab[i, j, 0] < upper[0] and
    #             lower[1] < lab[i, j, 1] < upper[1] and
    #                 lower[2] < lab[i, j, 2] < upper[2]):
    # count += 1
    # percent = count/34980
    # print(percent_red)
        print(percent_green)
    # print(percent_green)
        if percent_red > 0.65:
            label = "color: red"
            color = (0, 0, 255)
            detected = True
            frame_count = 11
        elif percent_green > 0.45:
            label = "color: green"
            color = (0, 255, 0)
            detected = True
            frame_count = 11
        elif percent_blue > 0.55:
            label = "color: blue"
            color = (255, 0, 0)
            detected = True
            frame_count = 11

    cv2.putText(image, label, (20, 460),
                cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 2)
    cv2.imshow("video before", frame)
    cv2.imshow("after", image)
    cv2.imshow("roi", roi)
    if frame_count >= 200:
        detected = False
        label = "Detecting.."
        color = (200, 200, 200)
    # cv2.imshow("mask blue", mask_green)
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break
cap.release()
