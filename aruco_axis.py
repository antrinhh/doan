import cv2
import math

# Colors
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)


def draw_axis(img, start_pts, img_pts):
    start_point = list(start_pts[0].ravel().astype(int))
    end_point_x = list(img_pts[0].ravel().astype(int))
    end_point_y = list(img_pts[1].ravel().astype(int))
    end_point_z = list(img_pts[2].ravel().astype(int))

    cv2.arrowedLine(img, start_point, end_point_x, RED, 2)
    cv2.arrowedLine(img, start_point, end_point_y, GREEN, 2)
    cv2.arrowedLine(img, start_point, end_point_z, BLUE, 2)

    end_point_x[0] = end_point_x[0] + 10
    end_point_y[1] = end_point_y[1] - 10
    end_point_z[1] = end_point_z[1] + 10
    end_point_z[0] = end_point_z[0] - 10

    cv2.putText(img, 'x', end_point_x, cv2.FONT_HERSHEY_PLAIN,
                0.8, RED, 1, cv2.LINE_AA)
    cv2.putText(img, 'y', end_point_y, cv2.FONT_HERSHEY_PLAIN,
                0.8, GREEN, 1, cv2.LINE_AA)
    cv2.putText(img, 'z', end_point_z, cv2.FONT_HERSHEY_PLAIN,
                0.8, BLUE, 1, cv2.LINE_AA)


def show_distance(frame, H=None):
    if H is not None:
        x, y, z = H[:3, 3].flatten()
        distance = math.sqrt(x**2+y**2+z**2)
        cv2.putText(frame, f"distance: {distance:.3f}cm", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def show_matrix(frame, H=None):
    if H is not None:
        start_y = 30
        dy = 20
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(H.shape[0]):
            text = f"{H[i][0]: .2f} {H[i][1]: .2f} {H[i][2]: .2f} {H[i][3]: .2f}"
            y = start_y + i * dy
            cv2.putText(frame, text, (410, y), cv2.FONT_HERSHEY_PLAIN,
                        1, (0, 255, 0), 2)
