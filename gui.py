"""
    GUI Modules
"""

import cv2

class UserInputGUI(object):
    """ Displays a question and process the user input as an  video screen overlay """
    def __init__(self, text, callback):
        self.text = text
        self.input = ""
        self._cb = callback

    def draw(self, frame):
        """ Draws the current text buffer and user input in frame """
        pos = (int(frame.shape[0]/2.0), int(frame.shape[1]/2.0))
        cv2.putText(frame, self.text, pos, cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255, 0.8), 6,cv2.LINE_AA)

        pos = (int(frame.shape[0]/2.0), int(frame.shape[1]/2.0) + 50)
        cv2.putText(frame, self.input, pos, cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255, 0.8), 5)

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


