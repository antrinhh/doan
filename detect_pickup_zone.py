import cv2 as cv
import numpy as np
from helper_func import extract_red, extract_blue, extract_green, adjust_gamma, mask_3_colors, morp_noise, gray_3_colors, is_closed_contour, load_calibration
from matrixes import Homogeous_end_to_cam

ZONE_SIZE = 25
ZONE_DIMENSION = np.array([[ZONE_SIZE/2, -ZONE_SIZE/2, 0], [ZONE_SIZE/2, ZONE_SIZE/2, 0], [-ZONE_SIZE/2, ZONE_SIZE/2, 0], 
                        [-ZONE_SIZE/2, -ZONE_SIZE/2, 0]], dtype=float)

def arm_scan():
    return True

lower_red = np.array([20, 140, 120])
upper_red = np.array([255, 230, 238])
# green LAB range
lower_green = np.array([0, 0, 126])
upper_green = np.array([255, 127, 255])
# blue LAB range
lower_blue = np.array([0, 0, 0])
upper_blue = np.array([132, 138, 109])


def DetectColor(image):
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    scale = 1.2
    hsv[:, :, 1] = hsv[:, :, 1]*scale
    image = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    roi = image[184:294, 247:343]
    lab = cv.cvtColor(roi, cv.COLOR_BGR2LAB)

    mask_red = cv.inRange(lab, lower_red, upper_red)
    mask_green = cv.inRange(lab, lower_green, upper_green)
    mask_blue = cv.inRange(lab, lower_blue, upper_blue)
    total_pixels = roi.shape[0]*roi.shape[1]
    percent_red = cv.countNonZero(mask_red) / total_pixels
    percent_green = cv.countNonZero(mask_green)/total_pixels
    percent_blue = cv.countNonZero(mask_blue)/total_pixels
    # cv.imshow("roi", roi)
    # cv.imshow("green's mask", mask_green)
    # cv.imshow("blue's mask", mask_blue)
    # cv.imshow("red's mask", mask_red)
    if percent_red > 0.75:
        return "red", (0, 0, 255)
    elif percent_green > 0.75:
        return "green", (0, 255, 0)
    elif percent_blue > 0.6:
        return "blue", (255, 0, 0)
    else:
        return "unknown", (150, 150, 150)


def detect_pickup_zone(frame, min_area=300):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    mask = cv.inRange(gray, 100, 200)
    contours, _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    box = []
    for contour in contours:
        area = cv.contourArea(contour)
        if area < min_area:
            continue
        esp = 0.02 * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, esp, True)
        if len(approx) == 4:
            sorted_pts = sort_contour_points(approx)
            # Draw and label
            cv.drawContours(frame, [approx], -1, (0, 250, 250), 3)
            for j, (x, y) in enumerate(sorted_pts):
                cv.putText(frame, str(j), (x + 5, y - 5), cv.FONT_HERSHEY_SIMPLEX,
                           0.5, (0, 0, 255), 1, cv.LINE_AA)
            box = cv.boundingRect(contour)
            return sorted_pts, box, mask
    
    return [], [], mask 

def sort_contour_points(pts):
    pts = pts.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")

    # Sum and difference
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]      
    rect[2] = pts[np.argmax(s)]       
    rect[1] = pts[np.argmin(diff)]    
    rect[3] = pts[np.argmax(diff)]  

    return rect.astype(int)

def distance_to_zone(points, cam_matrix, dist_coeffs):
    distance_to_zone = 0
    val, rv, tv = False, None, None
    if len(points) == 4:
        try:
            val, rv, tv = cv.solvePnP(ZONE_DIMENSION, points, cam_matrix, dist_coeffs)
            if val: 
                distance_to_zone = np.linalg.norm(tv)
                # print("Rotation:\n", rv)
                # print("Distance to zone:", distance_to_zone)
        except cv.error as e:
                print("solvePnP error:", e)
    return val, rv, tv

def main():
    vid = cv.VideoCapture(1)
    cam_matrix, dist_coeffs = load_calibration()
    retval = False
    distance = 0
    zones = 0

    while True:
        ret, frame = vid.read()
        frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
        
        points, mask = detect_pickup_zone(frame)
        points = np.array(points, dtype=np.float32)
        
        distance, retval, rvec, tvec = distance_to_zone(points, cam_matrix, dist_coeffs)
        if retval:
            zones += 1


        cv.imshow("Pickup Zone Detection", mask)
        cv.imshow("frame", frame)
        if cv.waitKey(50) == ord('q'):
            break
        # elif cv.waitKey(50) == ord('p'):
        #     cv.waitKey(-1)
    vid.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()