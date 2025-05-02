import numpy as np
from math import sin, cos, atan2, sqrt, degrees, radians, pi

d1 = 130
a2 = 140
a3 = 140
a4 = 75


def ForwardKinematics(q1, q2, q3, q4):
    q4 = 2*pi-q4
    H = np.array([[cos(q1)*cos(q2-q3-q4), -cos(q1)*sin(q2-q3-q4), sin(q1), a2*cos(q1)*cos(q2)+a3*cos(q1)*cos(q2-q3-q4)+a4*cos(q1)*cos(q2-q3-q4)],
                  [sin(q1)*cos(q2-q3-q4), -sin(q1)*sin(q2-q3-q4), -cos(q1), a2*sin(q1)
                   * cos(q2)+a3*sin(q1)*cos(q2-q3-q4)+a4*sin(q1)*cos(q2-q3-q4)],
                  [sin(q2-q3-q4), cos(q2-q3-q4), 0, d1+a2 *
                   sin(q2)+a3*sin(q2-q3)+a4*sin(q2-q3-q4)],
                  [0, 0, 0, 1]], dtype=np.float32)
    return H[0][3], H[1][3], H[2][3]


def InverseKinematics(x, y, z):
    q1 = atan2(y, x)
    r = sqrt(x**2+y**2)-a4
    D = (r**2+(z-d1)**2 - a2**2-a3**2)/(2*a2*a3)
    q3 = atan2(sqrt(1-D**2), D)

    alpha = atan2(a3*sin(q3)/r, (a2+a3*cos(q3))/r)
    beta = atan2(z-d1, r)
    q2 = alpha+beta
    q4 = q3 - alpha-beta
    return q1, q2, q3, q4


def main():
    q1_test, q2_test, q3_test, q4_test = InverseKinematics(300, 0, 250)
    x_test, y_test, z_test = ForwardKinematics(
        q1_test, q2_test, q3_test, q4_test)
    print(f"q1 = {degrees(q1_test)}\nq2 = {degrees(q2_test)}\nq3 = {degrees(q3_test)}\nq4 = {degrees(q4_test)}")
    print(f"x = {x_test}\ny = {y_test}\nz = {z_test}")


if __name__ == "__main__":
    main()
