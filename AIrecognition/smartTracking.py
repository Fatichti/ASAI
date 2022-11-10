import cv2                              # On importe toutes les librairies
import socket
import numpy as np
import os
import math
import struct

cam = cv2.VideoCapture(0)               # On initialise la capture video OpenCV (ici Pi Camera)
                
THRESHOLD = 0.25                        # Score minimum pour la détection

SHOW_IMAGE_DETECTION = True             # Pour afficher sur l'écran la caméra et la détection en Live
MODE_MATCHING = True                    # Pour effectuer l'opération de matching par OpenCV
MODE_AUTO_ADAPT_DIRECTION = True        # Pour calculer l'azimut et ajuster dynamiquement l'angle du servo (attaché à la caméra)
MODE_AUTO_ADAPT_TEMPLATE = False        # Pour ajuster dynamiquement le template à chaque détection correcte
MODE_SEND_AZIMUT = True                 # Pour envoyer l'azimut calculé au servo à travers une socket HTTP


PATH_DATA_FOLDER = "/home/fabienpi/Documents/UV_ASAI/data/recognition/"         # Chemin du dossier où se trouve les fichiers annexes nécessaires
TEMPLATE_IMG_NAME = "template.png"                                              # Nom dédié au template de détection

POSITION_OUTPUT_VIDEO = [500,50]        # Pour spécifier l'emplacement sur l'écran de la visualisation de la caméra
DISTANCE_FOCAL_CAM = 0.0036             # Distance focale de 3.6 mm, provenant de la datasheet  
LARGEUR_PIXEL_CAM = 1.4 * pow(10, -6)   # Largeur d'un pixel de la caméra de 1.4 micrometre, provenant de la datasheet 

if MODE_SEND_AZIMUT:
    HOST = "10.100.252.207"                                     # Adresse IP du serveur d'écoute pour la socket
    PORT = 6789                                                 # Port du serveur d'écoute pour la socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # On créer une socket
    s.connect((HOST, PORT))                                     # On créer une connexion


""" 
Pour simplifier la compréhension et la manipulation des détections,
j'ai défini une zone de détection sous la forme d'un objet.
Cette objet est déclaré par la classe suivante (zone).
La zone de détection contient alors des attributs comme des coordonées, une hauteur/largeur, une vitesse, accélération...
Et des méthodes pour calculer sa différence de position, sa vitesse ou encore son accélération lorsque cette zone se déplace 
"""

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

    def setLargeur(self, largeur):
        self.largeur = largeur

    def setHauteur(self, hauteur):
        self.hauteur = hauteur

    def calculNewDiff(self, newCoordX, newCoordY):
        diffX = newCoordX - self.coordX
        diffY = newCoordY - self.coordY
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
    global zoneDetection, init, initZoneMatch, CENTRE_IMG_CAM_X, templateImg        # On initialise des variables globales au programme
    init = True
    initZoneMatch = True
    while True:
        ret, frame = cam.read()                                                     # On capture chaque frame de la caméra
        
        if cv2.waitKey(25) & 0xFF == ord('q'):                                      # Quand on appuye sur q, on arrête le programme
            print("\n")
            break

        if ret:
            if init:
                coordROI = cropping(frame)                                          # Lors de la première frame réçu, on effectue un cropping (on choisi notre objet de référence dans la première image)
                if coordROI == (0,0,0,0):
                    break
                templateImg = cv2.imread(PATH_DATA_FOLDER + TEMPLATE_IMG_NAME)      # On enregistre l'image croppée comme template et on défini les paramètres de largeur/hauteur de la zone en conséquent
                shape = templateImg.shape
                zoneDetection.setHauteur(shape[0])
                zoneDetection.setLargeur(shape[1])
                CENTRE_IMG_CAM_X = frame.shape[1] / 2                               # Pour le calcul de l'azimut, on a besoin du centre de l'image de la caméra
                zoneDetection.coordX = coordROI[0]
                zoneDetection.coordY = coordROI[1]
                init = False

            if MODE_MATCHING:
                coordZoneToScan = (zoneDetection.coordY - zoneDetection.deltaY, zoneDetection.coordY + zoneDetection.hauteur + zoneDetection.deltaY, zoneDetection.coordX - zoneDetection.deltaX, zoneDetection.coordX + zoneDetection.largeur + zoneDetection.deltaX)
                imgToShow = matchZone(frame, coordZoneToScan)                       # Après avoir difini la zone à scanner, on effectuer des calculs de match

            if MODE_AUTO_ADAPT_DIRECTION:
                azimutCam = calculAzimut()
                if MODE_SEND_AZIMUT:
                    sendDAzimut(azimutCam)                                          # Après avoir calculer l'azimut, on l'envoi à l'ESP32 au travers d'une socket
                print("Azimut = ", azimutCam)

            if SHOW_IMAGE_DETECTION:
                cv2.namedWindow("Caméra")
                cv2.moveWindow("Caméra", POSITION_OUTPUT_VIDEO[0], POSITION_OUTPUT_VIDEO[1])
                imgToShow = cv2.rotate(imgToShow, cv2.ROTATE_180)                   # On affiche les images dans un sens + 180°, ceci est du au fixation de la caméra par rapport au champ de vision, qui est retourné
                cv2.imshow("Caméra", imgToShow)


    cam.release()
    cv2.destroyAllWindows()         # On supprime les écrans dès qu'on quitte le programme


def matchZone(frame, coordDetectionToScan):
    """
    fonction : matchZone
    paramètres : frame [tableau numpy], coordDetectionToScan [tableau 1D]
    valeur retour : frame [tableau numpy] avec rectangle de détection
    description : 
        1) on récupère la largeur et la hauteur de la zone à scan
        2) si elle est plus petite que le template, on ne fais pas de calcul
        3) sinon, si un objet est détecté, on défini comme nouveau template, la zone détectée et on détermine sa position
        4) sinon, si pas d'object détecté, on calcul le match en prenant toute l'image de la Caméra d'origine (et pas une zone théorique)
    """

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
            imgToShow = drawDetection(frame, coordPt, (0, 255, 255))                        # On dessine la zone où se trouve l'objet detecté
            imgToShow = drawDetection(frame, calculNewZone(coordZone), (255, 255, 0))       # On dessine la zone de recherche de détection
        else:
            imgToScan = frame
            isObjectDetected, pt = matchTemplate(templateImg, imgToScan)
            if isObjectDetected:
                coord = (pt[1], pt[0], pt[1] + zoneDetection.largeur, pt[0] + zoneDetection.hauteur)
                zoneDetection.coordX = pt[1]
                zoneDetection.coordY = pt[0]
                drawDetection(frame, coord, (0, 255, 255))
            imgToShow = frame
        
        return imgToShow            # On retourne soit l'image avec les zones trouvées dessus
    else:
        return frame                # Soit, l'image d'origine sans zones


def setNewTemplate(frame, coordPtForTemplate):
    """
    fonction : setNewTemplate
    paramètres : frame [tableau numpy], coordPtForTemplate [tableau 1D]
    valeur retour : aucune
    description : 
        1) on forme une frame à partir des coordonées de la zone où se trouve l'objet détectée
        2) on l'enregistre en tant que nouveau template
        3) on met à jour la largeur et la hauteur de la zone de détection
        4) sinon, si pas d'object détecté, on calcul le match en prenant toute l'image de la Caméra d'origine (et pas une zone théorique)
    """

    img_raw= frame[coordPtForTemplate[1]:coordPtForTemplate[3], coordPtForTemplate[0]:coordPtForTemplate[2]]
    cv2.imwrite(PATH_DATA_FOLDER + TEMPLATE_IMG_NAME,img_raw)
    zoneDetection.setHauteur(coordPtForTemplate[3] - coordPtForTemplate[1])
    zoneDetection.setLargeur(coordPtForTemplate[2] - coordPtForTemplate[0])


def calculNewZone(coord):
    """
    fonction : calculNewZone
    paramètres : coord [tableau 1D]
    valeur retour : coordZone[tableau 1D]
    description : 
        1) on initialise les coordonées de la zone de détection pour la première image
        2) pour la seconde, on défini la vitesse et l'accélération
        3) on met à jour alors ses coordonées
        4) on calcule ensuite les nouvelles coordonées de la zone de détection
    """
    
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
    """
    fonction : drawDetection
    paramètres : frame [tableau numpy], coord [tableau 1D], rgb [tuples (couleur rouge, vert, bleu)]
    valeur retour : frame [tableau numpy]
    description : 
        1) on dessine un rectangle avec les coordonées et le tuple de couleur définis
    """
    cv2.rectangle(frame, (coord[0], coord[1]), (coord[2], coord[3]), rgb, 2)
    return frame


def matchTemplate(template, imgActuelle):
    """
    fonction : matchTemplate
    paramètres : template [tableau numpy], imgActuelle [tableau 1D]
    valeur retour : objectDetecte [bool], coordObjetPt [tuple]
    description : 
        1) on tente de trouver une zone de match entre le template et la frame en cours
        2) on récuèpre l'endroit avec la valeur de détection la plus grande
        3) si on trouve un objet, on renvois les coordonnées du point sinon non
    """
    global zoneDetection
    res = cv2.matchTemplate(imgActuelle, template, cv2.TM_CCOEFF_NORMED)

    # Draw a rectangle around the matched region.
    pt = np.unravel_index(res.argmax(), res.shape)
    #print("score détection = ", round(res[pt],3), end="\r")
    if res[pt] > THRESHOLD:
        return True, pt
    else:
        return False, 0


def getSize(template):
    """
    fonction : getSize
    paramètres : template [tableau numpy]
    valeur retour : (hauteur, largeur) [tuple]
    description : 
        1) on récupère les dimensions du template, sa hauteur et sa largeur
    """
    h, w, _ = template.shape
    return (h,w)


def cropping(frame):
    """
    fonction : cropping
    paramètres : frame [tableau numpy]
    valeur retour : roi [tuple]
    description : 
        1) on utilise un utilitaire OpenCV pour afficher une image et choisir une zone où se trouve l'objet voulu
        2) on détermine alors le template comme l'image avec sa hauteur et largeur défini par ses coordonnées
    """
    img_raw = frame
    roi = cv2.selectROI(img_raw)

    print("Coordonnées de la zone choisie : ", roi)

    cv2.waitKey(0)                                                                                  # Dès qu'on appuye une touche, on arrête (entrer -> valider, c -> annuler)

    if(roi != (0,0,0,0)):
        roi_cropped = img_raw[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]       # On en determine une image
        cv2.imshow("ROI", roi_cropped)                                                              # On va laisser l'image template affiché en dehors de la fenêtre de détection
        cv2.destroyWindow("ROI selector")                                                           # Mais on supprime l'image avant croppage, inutile
        cv2.imwrite(PATH_DATA_FOLDER + TEMPLATE_IMG_NAME,roi_cropped)
    else:
        print("Aucun image choisie, abondon")
    return roi


def calculAzimut():
    """
    fonction : calculAzimut
    paramètres : aucun
    valeur retour : azimut [float]
    description : 
        1) on calcul l'azimut en fonction du centre de la caméra et du centre de la zone de détection
    """
    centreZoneX = (zoneDetection.coordX + zoneDetection.largeur/2)
    azimut = math.atan(((CENTRE_IMG_CAM_X - centreZoneX) * LARGEUR_PIXEL_CAM )/ DISTANCE_FOCAL_CAM)
    return azimut


def sendDAzimut(angle):
    """
    fonction : sendDAzimut
    paramètres : angle [float]
    valeur retour : aucune
    description : 
        1) on tente d'envoyer l'angle sur la socket, on affiche uniquement une erreur si on arrive pas à transmettre
    """
    try:
        angle = bytearray(struct.pack("f", angle))
        s.sendall(angle)
    except:
        print("ERROR ❌\nImpossible d'envoyer l'angle.")


os.system('clear')          # On efface la console pour plus de clareté

zoneDetection = zone()      # On créer un objet pour la zone de détection

main()                      # On lance le programme