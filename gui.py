#!/usr/local/bin/python
#  coding: utf-8
"""
    GUI Modules
"""

import cv2
import random

TEXTS = [
    ["ANONYM","UEBERWACHT","ANDERS","GLEICH","BIN MIR"],
    ["ABER","UND","NICHT","TROTZDEM","OBWOHL","SONDERN","ODER"],
    ["TRAURIG","SICHER","BEKANNT","UNBEKANNT","AEHNLICH"],
]

class UserInputGUI(object):
    """ Displays a question and process the user input as an  video screen overlay """
    def __init__(self, callback=None):
        self.texts = ["ANONYM","ABER","BEKANNT"]
        self.input = ""
        self._cb = callback
        self.debug_text = ""
    def draw(self, frame):
        """ Draws the current text buffer and user input in frame """
        pos = (750,440)
        cv2.putText(frame, self.texts[0], pos, cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255, 0.8), 6,cv2.LINE_AA)
        pos = (750,550)
        cv2.putText(frame, self.texts[1], pos, cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255, 0.8), 6,cv2.LINE_AA)
        pos = (750,700)
        cv2.putText(frame, self.texts[2], pos, cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255, 0.8), 6,cv2.LINE_AA)
        
        pos = (300,1000)
        cv2.putText(frame, self.debug_text, pos, cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255, 0.8), 6,cv2.LINE_AA)


    def process_key(self, key):
        """
          handles the input if gui is displayed
        """
        if key == 13 or key == 10:
            #enter pressed
            self._cb(self.input)
            self.input = ""
        elif key == 8:
            #delete one char
            self.input = self.input[:-1]
        else:
            self.input += chr(key)
        return True

    def switch_text(self, segment_id):
        self.texts[segment_id] = random.choice(TEXTS[segment_id])

