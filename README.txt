instructions for the interactive installation python software

Requirements:
 - Python 2.6.+
 - OpenCV 3.0 (also works with 2.x)
 - numpy 1.9.1

Configuration:
 - All configuration is done in settings.py
 there are the following options:
    CASCADE_DIR = "./xmls/" 
        - path to the xml configuration files for the face detection algorithm
    VIDEO_DEVICE = 0 
        - choose number of the input video device (webcam, external camera)
    DEBUG = False  
        - set to True to enable debugging mode

Run programm:
 command: python main.py        