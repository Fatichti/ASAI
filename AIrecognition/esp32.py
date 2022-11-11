from machine import Pin, PWM                # On importe toutes les librairies
import network, socket
import struct


servo = Pin(13, Pin.OUT)                    # On initialise notre servo sur le pin dédié, ici 13
servoPwm = PWM(servo)
servoPwm.freq(50)
angleServo = 80
angleMaxServo = 120
angleMinServo = 20
vitesseMaxServo = 1
servoPwm.duty(angleServo)
variationAngleServo = 3.0



def connectToWifi():
    """
    fonction : connectToWifi
    paramètres : aucun
    valeur retour : connexionEtablie [bool]
    description : 
        1) on tente de se connecter au wifi
        2) on affiche si on est connecté et on renvoi true
    """
    station = network.WLAN(network.STA_IF)
    station.active(True)
    try:
        station.connect("PPI-IMTNE", "PPI2022SN")
        if station.isconnected():
            print("SUCCESS : Connected to wifi, info :", station.ifconfig())
            return [True, station.ifconfig()]
        else:
            print("ERROR : Can't connect to Wifi, wait few seconds and try again")
            return [False]
    except:
        station.disconnect()
        return [False]


def getAzimut():
    """
    fonction : getAzimut
    paramètres : aucun
    valeur retour : aucune
    description : 
        1) on recoit la valeur de l'azimut sur la socket de smartTracking
        2) on en déduit la valeur de l'angle du servo à adapter
    """
    index = 1
    wifiStatus = connectToWifi()
    if wifiStatus[0]:
        s = socket.socket()	                                    # On créer une socket 
        s.bind(( "", 6789 ))
        s.listen(0)
        print("SUCCESS : Bin network")
        
        while True:
            try:
                client, addr = s.accept()
                print("SUCCESS : Client connected : ", addr)
            except:
                break

            while True:
                content = client.recv(1024)
                 
                if len(content) == 0:
                   break
         
                else:
                    requete = struct.unpack("f", content)[0]    # On recoit l'angle dans une structure que l'on extrait
                    print("Azimut received n°", index, " = ", requete)
                    calculValueServo(requete)
                    index +=1                                   # l'index sert juste à permetre de comprendre que l'on vient de recevoir une nouvelle valeur à chaque fois
                
                              
def calculValueServo(angleAzimut):
    """
    fonction : calculValueServo
    paramètres : angleAzimut [float]
    valeur retour : aucune
    description : 
        1) on calculer l'angle du servo à appliquer en fonction de l'angle azimut reçu
    """
    global angleServo
    
    angleServo += angleAzimut * (-60)
    if angleServo > angleMaxServo: angleServo = angleMaxServo
    elif angleServo < angleMinServo: angleServo = angleMinServo
    print("Angle servo = ", angleServo)
    servoPwm.duty(int(angleServo))
    
        
getAzimut()
    


