import numpy as np
import os
import cv2 as cv
import glob
import matplotlib.pyplot as plt

def calibrate(showPics = True):
    root = os.getcwd()
    calibrationDir = os.path.join(root, 'chessBoard')
    imgPathList = glob.glob(os.path.join(calibrationDir, '*.jpg'))

    nRows = 6
    nCols = 8
    termCriteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    worldPtsCur = np.zeros((nRows * nCols, 3), np.float32)
    worldPtsCur[:,:2] = np.mgrid[0:nRows, 0:nCols].T.reshape(-1, 2)
    worldPtsList = []
    imgPtsList = []

    print(f"Found {len(imgPathList)} images.")
    print(imgPathList)

    # Find corners
    for curImgPath in imgPathList:
        imgBGR = cv.imread(curImgPath)
        if imgBGR is None:
            print("Nothing")
        imgGray = cv.cvtColor(imgBGR, cv.COLOR_BGR2GRAY)
        cornersFound, cornersOrg = cv.findChessboardCorners(imgGray, (nRows, nCols), None)

        if cornersFound == True:
            worldPtsList .append(worldPtsCur)
            cornersRefined = cv.cornerSubPix(imgGray, cornersOrg, (11, 11), (-1, -1), termCriteria)
            imgPtsList.append(cornersRefined)
            if showPics:
                cv.drawChessboardCorners(imgBGR, (nRows, nCols), cornersRefined, cornersFound)
                cv.imshow('ChessBoard', imgBGR)
                cv.waitKey(500)
    if cv.waitKey(16) == ord('q'):
        cv.destroyAllWindows()

    repError, camMatrix, distCoeff, rvecs, tvecs = cv.calibrateCamera(
        worldPtsList, imgPtsList, imgGray.shape[::-1], None, None)
    print("Camera Matrix: \n", camMatrix)
    print("Reproj Error (pixels): {:.4f}".format(repError))

    curFolder = os.path.dirname(os.path.abspath(__file__))
    paramPath = os.path.join(curFolder, "calibration.npz")
    np.savez(paramPath, repError = repError, camMatrix = camMatrix, distCoeff = distCoeff, rvecs = rvecs, tvecs = tvecs)

    return camMatrix, distCoeff

def runCalibration():
    calibrate(showPics=True)

def takePics():
    root = os.getcwd()
    save_dir = os.path.join(root, 'chessBoard')
    cap = cv.VideoCapture(1)
    img_count = 0

    while True:
        ret, frame = cap.read()
        frame = cv.resize(frame, (640, 480))
        # frame = cv.flip(frame)
        cv.imshow('Smile', frame)

        key = cv.waitKey(16) & 0xFF  # Wait for key press
        
        if key == ord('q'):  # Press 'q' to exit
            break
        elif key == ord('c'):  # Press 'c' to capture
            img_path = os.path.join(save_dir, f"image_{img_count:03d}.jpg")
            cv.imwrite(img_path, frame)
            print(f"Saved: {img_path}")
            img_count += 1
    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    runCalibration()


