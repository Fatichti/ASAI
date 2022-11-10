# General information
- **UV** : ASAI
- **Name** : Fabien Plouvier 
- **Date** : 10/10/2022 -> 09/11/2022

📌This branch of our Git repository corresponds to my work for AI recognition.
  
## What is the context?
🛠️The specifications were :  
1. The Pi Camera captures video in real time  
2. Each frame is analysed by a Python program on the Raspberry
3. The program is able to track an object in the camera
4. A connected servo adjusts its viewing angle to focus on the traced object
        
## What are the tools available?
**The KIT : Raspberry pi 4 card  + Servo + ESP32**  
![KitRecognition](data/gitReadme/kitRecognition.gif)  


## What is in the branch?
To complete these specifications, I created the folder 📂 **"AIRecognition"** which contains the Python recognition script.

👀For a better understanding, here is **the tree structure** of this branch:  
```bash
├── readme.md
├── data                                # The data necessary for the operation of the scripts and for the structure of the git
│   ├── gitReadme                       # For the structure of the git
│   ├── yolo                            # To get started with Yolo
│   └── recognition                     # For the main recognition
└── AIRecognition
    ├── smartTracking.py                # Main program: camera + recognition + matching + servo
    └── yolo.py                         # Program to get started with yolo
```

## How to install and run the scripts?
⚠️To be able to use our work correctly, please follow the steps for **installing** and **running** the files/scripts.

### Installation

1. Clone the folder in your directory: 
```git
git clone https://github.com/Fatichti/ASAI.git
```

2. Change the current git branch
```git
git checkout AI-Recognition
```

3. Install the yolo files (large files)  
Links :
    - [yolov3.weights](https://pjreddie.com/media/files/yolov3.weights)
    - [yolov2.cfg](https://opencv-tutorial.readthedocs.io/en/latest/_downloads/10e685aad953495a95c17bfecd1649e5/yolov3.cfg)
    - [coco.names](https://opencv-tutorial.readthedocs.io/en/latest/_downloads/a9fb13cbea0745f3d11da9017d1b8467/coco.names)  

    And put them in ``data/yolo`` folder.  

### Running
After adjusting the parameters of the scripts, launch any Python script :
```Bash
python AIRecogntion/smartTracking.py    # To start the main recognition program
```  
Or  
```Bash
python AIRecogntion/yolo.py              # To test yolo on an image
```