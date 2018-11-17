import cv2
import os

from settings import CASCADE_DIR, DEBUG

FACE_CASCADE = cv2.CascadeClassifier(os.path.join(CASCADE_DIR,
                                     "haarcascade_frontalface_default.xml"))

EYE_CASCADE = cv2.CascadeClassifier(os.path.join(CASCADE_DIR,
                                     "haarcascade_eye.xml"))

import numpy as np
def find_faces(frame):
    """
        Finds faces, eyes and set nose coordinates in frame
        returns list of faces [(y_coord_eyes, y_coord_nose, face_img, face_position),...]
    """

    faces = []
    b = 50
    detected_faces = FACE_CASCADE.detectMultiScale(frame, 1.3, 8)
    for x, y, w, h in detected_faces:
        maxY = int(round(h/1.8))
        if DEBUG:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0))
        headSegment = frame[y:y+maxY, x:x+w]
        # detect eyes
        eyes = EYE_CASCADE.detectMultiScale(headSegment) 
        midEyeY = 0
        for ex, ey,ew,eh in eyes:
            if DEBUG:
                cv2.rectangle(headSegment, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            midEyeY += ey + eh

        if len(eyes):
            midEyeY = int(midEyeY / len(eyes))
            midEyeY += b
            #midEyeY += y
        else:
            midEyeY = None
            continue
        
        noseY = int(h/5)
        if midEyeY:
            xn = x - b
            yn = y - b
            if xn < 0: xn = 0
            if yn < 0: yn = 0
            portrait = frame[yn:y+h+b,xn:x+w+b]
            faces.append([midEyeY, noseY, portrait, np.array([xn,yn])])

    return faces


