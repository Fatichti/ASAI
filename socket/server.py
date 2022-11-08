# echo-server.py

import socket
import sys, os

sys.path.append("/home/fabienpi/Documents/UV_ASAI")
from reconnaissance.visionCV import *


HOST = "10.100.252.90"  # Standard loopback interface address (localhost)
PORT = 6789  # Port to listen on (non-privileged ports are > 1023)
LIMIT_DATA = 1024


def init():
    os.system("clear")



init()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind((HOST, PORT))
        s.listen()
        print("SERVEUR ON ✅\n")
        conn, addr = s.accept()

        with conn:
            log(f"Connecté sur {addr} ✅\n")
            while True:
                data = conn.recv(LIMIT_DATA)
                if not data:
                    log("Aucune donnée reçu ❌")
                    break
                if "@" == data.decode('utf-8'):
                    log("@ reçu en appel ✅")
                    try:
                        takeImgFromPICam()
                        img = open(FILENAME,"rb")
                        b_img = img.read()
                        log("Taille img ")
                        conn.sendall(b_img)
                        s.shutdown()
                        log("Image envoyée avec succès ✅, taille : " + len(b_img))

                    except:
                        log("Fin traitement")
                        break

    except:
        print("SERVEUR OFF ❌\nPatientez un instant puis réessayer.")

    
        

