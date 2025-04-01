import cv2 as cv
import os
import numpy as np

# Define world's variables
cube_size = 2.5
# cube_points = np.array([
#     [0, 0, 0], [cube_size, 0, 0], [cube_size, cube_size, 0], [0, cube_size, 0],  # Base
#     [0, 0, cube_size], [cube_size, 0, cube_size], [cube_size, cube_size, cube_size], [0, cube_size, cube_size]  # Top
# ], dtype = float)

cube_points = np.array([[0, 0, 0], [cube_size, 0, 0], [cube_size, 0, -cube_size], [0, 0, -cube_size], [0, cube_size, 0], 
                        [cube_size, cube_size, 0], [cube_size, cube_size, -cube_size], [0, cube_size, -cube_size]], dtype=float)

axis = np.float32([
    [6, 0, 0], [0, 6, 0], [0, 0, 6]  # Extended axes for visibility
])

def load_calibration():
    param_path = os.path.join(os.getcwd(), 'calibration.npz')
    param_data = np.load(param_path)
    return param_data['camMatrix'], param_data['distCoeff']

def draw_axes(frame, cam_matrix, dist_coeffs, rvecs, tvecs, cube_corners):
    imgpts, _ = cv.projectPoints(axis, rvecs, tvecs, cam_matrix, dist_coeffs)
    origin = tuple(cube_corners[0].ravel().astype(int))
    frame = cv.line(frame, origin, tuple(imgpts[0].ravel().astype(int)), (0, 0, 255), 3)  # X (Red)
    frame = cv.line(frame, origin, tuple(imgpts[1].ravel().astype(int)), (0, 255, 0), 3)  # Y (Green)
    frame = cv.line(frame, origin, tuple(imgpts[2].ravel().astype(int)), (255, 0, 0), 3)  # Z (Blue)
    return frame

# Preprocessing to enhance edge detection
def preprocess_frame(frame, bbox):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Adaptive Histogram Equalization (CLAHE)
    clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # Reduce noise while keeping edges (Bilateral Filter)
    filtered = cv.bilateralFilter(gray, 9, 75, 75)

    # Canny Edge Detection with adaptive thresholding
    median_val = np.median(filtered)
    lower_thresh = int(max(0, 0.7 * median_val))
    upper_thresh = int(min(255, 1.3 * median_val))
    edges = cv.Canny(filtered, lower_thresh, upper_thresh)

    # Morphological Closing to connect broken edges
    kernel = np.ones((3, 3), np.uint8)
    edges = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel)

    return edges


# HSV Thresholding for Blue Cube
def threshold_cube(frame):
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv.inRange(hsv, lower_blue, upper_blue)

    # Use morphological closing to remove small holes inside the detected object
    kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)

    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    bbox = (0, 0, 0, 0)

    if contours:
        largest_contour = max(contours, key=cv.contourArea)
        if cv.contourArea(largest_contour) > 500:
            x, y, w, h = cv.boundingRect(largest_contour)
            bbox = (x, y, w, h)
            cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    return mask, bbox


# Find Cube Contours
def get_cube_contours(mask):
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contour_frame = np.zeros(mask.shape, dtype=np.uint8)
    cv.drawContours(contour_frame, contours, -1, 255, 1)

    best_approx = None
    for cnt in contours:
        if cv.contourArea(cnt) > 500:
            approx = cv.approxPolyDP(cnt, 0.02 * cv.arcLength(cnt, True), True)

            if 4 <= len(approx) <= 6:  # Accept quadrilateral or hexagonal shapes
                best_approx = approx.reshape(-1, 2)

    return best_approx, contours, contour_frame

def position_estimation(frame, cube_corners, cam_matrix, dist_coeffs):
    if cube_corners is None or cube_corners.shape != (5, 2):
        print("[ERROR] Cube corners are not in the expected shape!")  # Debugging
        return frame, None, None  # Ensure three values are returned

    retval, rvec, tvec = cv.solvePnP(cube_points[:4], cube_corners.astype(np.float32), cam_matrix, dist_coeffs, useExtrinsicGuess=False)

    if not retval:
        print("[ERROR] solvePnP failed!")  # Debugging
        return frame, None, None  # Ensure three values are returned

    frame = draw_axes(frame, cam_matrix, dist_coeffs, rvec, tvec, cube_corners)
    return frame, rvec, tvec

def main():
    cam_matrix, dist_coeffs = load_calibration()
    cap = cv.VideoCapture("D:/Prime/Playing/doan/data/red vid.MOV")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Cube Detection
        mask, bbox = threshold_cube(frame)
        processed = preprocess_frame(frame, bbox)

        # Edge Detection
        edges = cv.Canny(processed, 50, 150)

        # Contour Detection
        cube_corners, contours, contour_frame = get_cube_contours(mask)

        # Pose Estimation
        if cube_corners is not None:
            for i, corner in enumerate(cube_corners):
                cv.circle(frame, tuple(corner), 10, (0, 0, 255), -1)  # Draw the corner
                cv.putText(frame, str(i), tuple(corner + np.array([5, -5])), 
                        cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # Display index
            frame, rvec, tvec = position_estimation(frame, cube_corners, cam_matrix, dist_coeffs)
        
        # Display Results
        cv.imshow('HSV Threshold', mask)
        cv.imshow('Preprocessed', processed)
        cv.imshow('Canny Edges', edges)
        cv.imshow('Final Output', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
