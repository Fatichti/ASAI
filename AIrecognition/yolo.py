import cv2 as cv                        # On importe toutes les librairies
import numpy as np
import time


WHITE = (255, 255, 255)
img = None
img0 = None
outputs = None

URL_WEBCAM = 0
PATH_DATA_FOLDER = "/home/fabienpi/Documents/UV_ASAI/data/yolo"
YOLO_NAME = "yolov3.cfg"
CAT_NAME = "coco.names"
WEIGHTS_NAME = "yolov3.weights"
IMAGE_TESTYOLO_NAME = "horse.jpg"               # Si on veut analyser sur une seul image (conseillé)
USE_WEBCAM = False                              # Si on veut un flux vidéo en continu (non conseillé)


classes = open(PATH_DATA_FOLDER + CAT_NAME).read().strip().split('\n')      # On charge les noms des classes et obtenir des couleurs aléatoires
np.random.seed(42)
colors = np.random.randint(0, 255, size=(len(classes), 3), dtype='uint8')


# On spécifie les fichiers de configuration et de poids pour le modèle et charger le réseau.
net = cv.dnn.readNetFromDarknet(PATH_DATA_FOLDER + YOLO_NAME, PATH_DATA_FOLDER + WEIGHTS_NAME)
#net.setPreferableBackend(cv.dnn.DNN_BACKEND_INFERENCE_ENGINE)              # Non terminée et fonctionnelle, ceci avait pour but d'utiliser le stick intel neural compute
#net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)                             # Ce backend fonctionne
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)                         # Ce backend fonctionne


ln = net.getLayerNames()                                                    # On détermine la couche de sortie

ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

def load_image(path):
    """
    fonction : load_image
    paramètres : path [path]
    valeur retour : aucune
    description : 
        1) on charge une image et on récupère l'analyse yolo
    """                                                     
    global img, img0, outputs, ln

    img0 = cv.imread(path)
    img = img0.copy()

    blob = cv.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)

    net.setInput(blob)
    t0 = time.time()
    outputs = net.forward(ln)
    t = time.time() - t0

    outputs = np.vstack(outputs)

    post_process(img, outputs, 0.5)
    cv.imshow('window', img)
    cv.waitKey(0)


def post_process(img, outputs, conf):
    """
    fonction : post_process
    paramètres : img [tableau numpy], outputs [tableau 1D], conf [float]
    valeur retour : aucune
    description : 
        1) on récupère des informations de l'analyse comme le score, la classe et les coordonées des objets détectés
    """   
    H, W = img.shape[:2]

    boxes = []
    confidences = []
    classIDs = []

    for output in outputs:
        scores = output[5:]
        classID = np.argmax(scores)
        confidence = scores[classID]
        if confidence > conf:
            x, y, w, h = output[:4] * np.array([W, H, W, H])
            p0 = int(x - w//2), int(y - h//2)
            p1 = int(x + w//2), int(y + h//2)
            boxes.append([p0, int(w), int(h)])
            confidences.append(float(confidence))
            classIDs.append(classID)
            
    indices = cv.dnn.NMSBoxes(boxes, confidences, conf, conf-0.1)
    if len(indices) > 0:
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            color = [int(c) for c in colors[classIDs[i]]]
            cv.rectangle(img, (x, y), (x + w, y + h), color, 2)
            text = "{}: {:.4f}".format(classes[classIDs[i]], confidences[i])
            cv.putText(img, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        
def trackbar(x):
    """
    fonction : trackbar
    paramètres : x [float]
    valeur retour : aucune
    description : 
        1) on prépare les détections avec un seuil de confiance
        2) on appelle l'étape de l'analyse des détections
    """
    global img
    conf = x/100
    img = img0.copy()
    post_process(img, outputs, conf)
    cv.imshow('window', img)


def takeImgFromWebCam():
    """
    fonction : takeImgFromWebCam
    paramètres : aucun
    valeur retour : aucune
    description : 
        1) on peut récupéré un flux vidéos en continu au lieux d'une seul image (qui est par défaut)
        2) on appelle l'étape de l'analyse des détections
    """
    cap = cv.VideoCapture(URL_WEBCAM)
    while(True):
        ret, frame = cap.read()
        cv.imshow('frame',frame)
        cv.namedWindow('window')
        cv.createTrackbar('confidence', 'window', 50, 100, trackbar)

        if cv.waitKey(1) & 0xFF == ord('q'):
            cv.destroyAllWindows()
            break


if USE_WEBCAM:
    takeImgFromWebCam()
else:                                  
    cv.namedWindow('window')
    cv.createTrackbar('confidence', 'window', 50, 100, trackbar)

    load_image(PATH_DATA_FOLDER + IMAGE_TESTYOLO_NAME)
    cv.destroyAllWindows()
