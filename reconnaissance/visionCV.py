# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2


PATHIMG = "/home/fabienpi/Documents/UV_ASAI/data/"
FILENAME = PATHIMG + "templatev2.png"
RESOLUTION = [1024, 1024]


def log(msg):
    print("[VISION DEBUG] : ", msg)


def takeImgFromPICam():
    log("Initialisation camera ⏳")
    camera = PiCamera()
    
    # On change la résolution
    camera.resolution = (RESOLUTION[0], RESOLUTION[1])
    
    # On laisse un petit délai de 0.1 sec
    time.sleep(0.1)

    log("Capture image 📸")
    camera.capture(FILENAME)


takeImgFromPICam()