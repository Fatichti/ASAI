# Importing all necessary libraries
import cv2
import socket
import numpy as np
import os
import math
import struct

# Read the video from specified path
cam = cv2.VideoCapture(0) #"/home/fabienpi/Documents/UV_ASAI/data/")
                
THRESHOLDv2 = 0.25                   # Score minimum pour la détection

SHOW_IMAGE_DETECTION = True
MODE_MATCHING = True
MODE_AUTO_ADAPT_DIRECTION = True
MODE_AUTO_ADAPT_TEMPLATE = False
MODE_SEND_AZIMUT = True


PATH_DATA_FOLDER = "/home/fabienpi/Documents/UV_ASAI/data/"
OUTPUT_VIDEO_NAME = "video1.avi"
TEMPLATE_IMG_NAME = "template.png"

NUMBER_IMAGE_VIDEO = 10000            # Une valeur de -1 signifie sans limite
POSITION_OUTPUT_VIDEO = [500,50]
DISTANCE_FOCAL_CAM = 0.0036             # Distance focale de 3.6 mm     
LARGEUR_PIXEL_CAM = 1.4 * pow(10, -6)        # Largeur Pixel Cam 1.4 micrometre

if MODE_SEND_AZIMUT:
    HOST = "10.100.252.207"   # Standard loopback interface address (localhost)
    PORT = 6789  # Port to listen on (non-privileged ports are > 1023)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))


class zone:
    def __init__(self):
        self.coordX = 0
        self.coordY = 0
        self.largeur = 0
        self.hauteur = 0
        self.deltaX = 50
        self.deltaY = 50
        self.diffX = 0
        self.diffY = 0
        self.speedX = 0
        self.speedY = 0
        self.accX = 0
        self.accY = 0
        self.numberApparitionObjetDetected = 0

    def setLargeur(self, largeur):
        self.largeur = largeur

    def setHauteur(self, hauteur):
        self.hauteur = hauteur

    def calculNewDiff(self, newCoordX, newCoordY):
        diffX = newCoordX - self.coordX
        diffY = newCoordY - self.coordY
        #print("newCoordX/Y = (", newCoordX, ", ", newCoordY, ") et self coordX/Y = (", self.coordX, ", ", self.coordY, ")")
        return(diffX, diffY)

    def calculNewKDiff(self):
        self.diffX = self.diffX + self.accX
        self.diffY = self.diffY + self.accY

    def calculNewSpeed(self, newSpeedX, newSpeedY):
        self.speedX = newSpeedX
        self.speedY = newSpeedY

    def calculNewAccl(self, newDiffX, newDiffY):
        self.accX = newDiffX - self.diffX
        self.accY = newDiffY - self.diffY

    def calculNewCoord(self):
        self.coordX = self.coordX + self.diffX - self.deltaX
        self.coordY = self.coordY + self.diffY - self.deltaY



def main():
    global zoneDetection, init, initZoneMatch, CENTRE_IMG_CAM_X, templateImg
    init = True
    initZoneMatch = True
    while True:
        ret, frame = cam.read()
        if cv2.waitKey(25) & 0xFF == ord('q'):
            
            print("\n")
            break

        if ret:
            if init:
                coordROI = cropping(frame)
                if coordROI == (0,0,0,0):
                    break
                templateImg = cv2.imread(PATH_DATA_FOLDER + TEMPLATE_IMG_NAME)
                shape = templateImg.shape
                zoneDetection.setHauteur(shape[0])
                zoneDetection.setLargeur(shape[1])
                CENTRE_IMG_CAM_X = frame.shape[1] / 2   # Coordonnée sur le plan X du centre de l'image de la caméra
                zoneDetection.coordX = coordROI[0]
                zoneDetection.coordY = coordROI[1]
                init = False

            if MODE_MATCHING:
                #imgToScan = frame[zoneDetection.coordY - zoneDetection.deltaY:zoneDetection.coordY + zoneDetection.hauteur + zoneDetection.deltaY,zoneDetection.coordX - zoneDetection.deltaX:zoneDetection.coordX + zoneDetection.largeur + zoneDetection.deltaX,:]
                coordZoneToScan = (zoneDetection.coordY - zoneDetection.deltaY, zoneDetection.coordY + zoneDetection.hauteur + zoneDetection.deltaY, zoneDetection.coordX - zoneDetection.deltaX, zoneDetection.coordX + zoneDetection.largeur + zoneDetection.deltaX)
                imgToShow = matchZone(frame, coordZoneToScan)

                #isObjectDetected, pt = matchTemplate(templateImg, imgToScan)
                
                """ if isObjectDetected:
                    coordPt = (pt[1] + zoneDetection.coordX - zoneDetection.deltaX, pt[0] + zoneDetection.coordY - zoneDetection.deltaY, pt[1] + zoneDetection.largeur + zoneDetection.coordX - zoneDetection.deltaX, pt[0] + zoneDetection.hauteur + zoneDetection.coordY - zoneDetection.deltaY)
                    coordZone = (pt[1] + zoneDetection.coordX, pt[0] + zoneDetection.coordY, pt[1] + zoneDetection.largeur + zoneDetection.coordX, pt[0] + zoneDetection.hauteur + zoneDetection.coordY)
                    if MODE_AUTO_ADAPT_TEMPLATE:
                        setNewTemplate(frame, coordPt)
                    imgToShow = drawDetection(frame, coordPt, (0, 255, 255))
                    imgToShow = drawDetection(frame, calculNewZone(coordZone), (255, 255, 0))
                else:
                    imgToScan = frame
                    isObjectDetected, pt = matchTemplate(templateImg, imgToScan)
                    if isObjectDetected:
                        coord = (pt[1], pt[0], pt[1] + zoneDetection.largeur, pt[0] + zoneDetection.hauteur)
                        zoneDetection.coordX = pt[1]
                        zoneDetection.coordY = pt[0]
                        drawDetection(frame, coord, (0, 255, 255))
                    imgToShow = frame """


            if MODE_AUTO_ADAPT_DIRECTION:
                azimutCam = calculAzimut()
                if MODE_SEND_AZIMUT:
                    sendDAzimut(azimutCam)
                print("Azimut = ", azimutCam)


            if SHOW_IMAGE_DETECTION:
                cv2.namedWindow("Caméra")
                cv2.moveWindow("Caméra", POSITION_OUTPUT_VIDEO[0], POSITION_OUTPUT_VIDEO[1])
                imgToShow = cv2.rotate(imgToShow, cv2.ROTATE_180)
                cv2.imshow("Caméra", imgToShow)


    
    # Release all space and windows once done
    cam.release()
    cv2.destroyAllWindows()


def matchZone(frame, coordDetectionToScan):
    global templateImg
    hauteur = coordDetectionToScan[1] - coordDetectionToScan[0]
    largeur = coordDetectionToScan[3] - coordDetectionToScan[2]

    testHauteurLargeur = (hauteur >= templateImg.shape[0] and largeur >= templateImg.shape[1])
    testCoord = (coordDetectionToScan[0] >= 0 and coordDetectionToScan[2] >= 0)

    if testHauteurLargeur and testCoord:
        imgToScan = frame[coordDetectionToScan[0]:coordDetectionToScan[1], coordDetectionToScan[2]:coordDetectionToScan[3],:]
        isObjectDetected, pt = matchTemplate(templateImg, imgToScan)

        if isObjectDetected:
            coordPt = (pt[1] + zoneDetection.coordX - zoneDetection.deltaX, pt[0] + zoneDetection.coordY - zoneDetection.deltaY, pt[1] + zoneDetection.largeur + zoneDetection.coordX - zoneDetection.deltaX, pt[0] + zoneDetection.hauteur + zoneDetection.coordY - zoneDetection.deltaY)
            coordZone = (pt[1] + zoneDetection.coordX, pt[0] + zoneDetection.coordY, pt[1] + zoneDetection.largeur + zoneDetection.coordX, pt[0] + zoneDetection.hauteur + zoneDetection.coordY)
            if MODE_AUTO_ADAPT_TEMPLATE:
                setNewTemplate(frame, coordPt)
            imgToShow = drawDetection(frame, coordPt, (0, 255, 255))
            imgToShow = drawDetection(frame, calculNewZone(coordZone), (255, 255, 0))
        else:
            imgToScan = frame
            isObjectDetected, pt = matchTemplate(templateImg, imgToScan)
            if isObjectDetected:
                coord = (pt[1], pt[0], pt[1] + zoneDetection.largeur, pt[0] + zoneDetection.hauteur)
                zoneDetection.coordX = pt[1]
                zoneDetection.coordY = pt[0]
                drawDetection(frame, coord, (0, 255, 255))
            imgToShow = frame
        
        return imgToShow
    else:
        return frame



def setNewTemplate(frame, coordPtForTemplate):
    img_raw= frame[coordPtForTemplate[1]:coordPtForTemplate[3], coordPtForTemplate[0]:coordPtForTemplate[2]]
    cv2.imwrite(PATH_DATA_FOLDER + TEMPLATE_IMG_NAME,img_raw)
    zoneDetection.setHauteur(coordPtForTemplate[3] - coordPtForTemplate[1])
    zoneDetection.setLargeur(coordPtForTemplate[2] - coordPtForTemplate[0])



def calculNewZone(coord):
    global zoneDetection, initZoneMatch
    if initZoneMatch:
        newDiffX, newDiffY = zoneDetection.calculNewDiff(coord[0], coord[1])
        zoneDetection.diffX = newDiffX
        zoneDetection.diffY = newDiffY
        initZoneMatch = False
    else:
        
        newDiffX, newDiffY = zoneDetection.calculNewDiff(coord[0], coord[1])
        zoneDetection.calculNewAccl(newDiffX, newDiffY)
        zoneDetection.calculNewKDiff()
        zoneDetection.diffX = newDiffX
        zoneDetection.diffY = newDiffY
        

    zoneDetection.calculNewCoord()
    
    coordZone = (zoneDetection.coordX - zoneDetection.deltaX, zoneDetection.coordY - zoneDetection.deltaY, zoneDetection.coordX + zoneDetection.largeur + zoneDetection.deltaX, zoneDetection.coordY + zoneDetection.hauteur + zoneDetection.deltaY)
    return coordZone


def drawDetection(frame, coord, rgb):
    cv2.rectangle(frame, (coord[0], coord[1]), (coord[2], coord[3]), rgb, 2)
    return frame


def matchTemplate(template, imgActuelle):
    global zoneDetection
    res = cv2.matchTemplate(imgActuelle, template, cv2.TM_CCOEFF_NORMED)

    # Draw a rectangle around the matched region.
    pt = np.unravel_index(res.argmax(), res.shape)
    #print("score détection = ", round(res[pt],3), end="\r")
    if res[pt] > THRESHOLDv2:
        return True, pt
    else:
        return False, 0


def getSize(template):
    # Store width and height of template in w and h
    h, w, _ = template.shape
    return (h,w)


def cropping(frame):

    #read image
    img_raw = frame
    #img_raw = cv2.rotate(img_raw, cv2.ROTATE_180)
    #select ROI function
    roi = cv2.selectROI(img_raw)

    #print rectangle points of selected roi
    print(roi)
    cv2.waitKey(0)

    if(roi != (0,0,0,0)):
        #Crop selected roi from raw image
        roi_cropped = img_raw[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
        #roi_cropped = img_raw[int(roi[1]+roi[3]):int(roi[1]), int(roi[0]+roi[2]):int(roi[0])]

        #show cropped image
        cv2.imshow("ROI", roi_cropped)
        cv2.destroyWindow("ROI selector")
        cv2.imwrite(PATH_DATA_FOLDER + TEMPLATE_IMG_NAME,roi_cropped)
    else:
        print("Aucun image choisie, abondon")

    return roi



def calculAzimut():
    centreZoneX = (zoneDetection.coordX + zoneDetection.largeur/2)
    azimut = math.atan(((CENTRE_IMG_CAM_X - centreZoneX) * LARGEUR_PIXEL_CAM )/ DISTANCE_FOCAL_CAM)
    return azimut


def sendDAzimut(angle):
    try:
        angle = bytearray(struct.pack("f", angle))
        s.sendall(angle)
    except:
        print("ERROR ❌\nImpossible d'envoyer l'angle.")




# On clear la console
os.system('clear')

# On créer un objet pour la zone
zoneDetection = zone()

main()