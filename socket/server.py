import socket                                               # On fait les importations nécessaires
import sys, os

HOST = "10.100.252.90"                                      # Adresse IP de celui qui va écouter, le serveur
PORT = 6789                                                 # Port d'écoute
LIMIT_DATA = 1024                                           # Limite de taille des données reçues en octets
PATHIMG = "/home/fabienpi/Documents/UV_ASAI/data/"          # On défini un chemin vers un dossier
FILENAME = PATHIMG + "templatev2.png" 

os.system("clear")                                          # Par souci de clareté, on efface le terminal en cours

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # On créer une socket 
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
                    log("Aucune donnée reçue ❌")
                    break
                if "@" == data.decode('utf-8'):
                    log("Signal @ reçu ✅")
                    try:
                        img = open(FILENAME,"rb")
                        b_img = img.read()
                        conn.sendall(b_img)
                        s.shutdown()
                        log("Image envoyée avec succès ✅, taille : " + len(b_img))

                    except:
                        log("Fin traitement")
                        break

    except:
        print("SERVEUR OFF ❌\nPatientez un instant puis réessayer.")

    
        

