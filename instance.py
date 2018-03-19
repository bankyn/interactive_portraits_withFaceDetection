"""
    Main Instance to display video in and output
"""

import numpy as np
import cv2
import os
import sys
from time import time

from gui import UserInputGUI
from user import MultiStripesUser, FaceDetectionUser 
from settings import DEBUG, VIDEO_DEVICE 


class Instance(object):
    def __init__(self):
        self.is_running = True
        self._cap = None
        self.window_height = 1080
        self.window_width = 1920
        # 1 fps initially
        self._speed = 1/25.0
        self._video = None
        self._gui = None
        self._current_user = None
        self.current_frame = None
        self.user_mode = True
        self.init(VIDEO_DEVICE)
    
    
    def set_fps(self, fps):
        """ callback for the fps trackbar """
        if fps <= 0:
            return
        self._speed = 1.0/fps
        
    def update_user_attribute(self, fn, value):
        if self._current_user is None:
            return 
        fn = getattr(self._current_user, fn)
        fn(value)

    def init(self, _video_device_id):
        self._cap = cv2.VideoCapture(_video_device_id)
        if not self._cap.isOpened():
            print "_cap open failed"
            sys.exit(1)

        frame1 = self.get_frame()
        #self.window_height, self.window_width, depth = frame1.shape

        # init control window with trackbars
        #cv2.namedWindow('anpassen')
        #cv2.createTrackbar('FPS', 'anpassen', 1, 25, self.set_fps)
        #cv2.createTrackbar('frames', 'anpassen', 1, 100,
        #        lambda l: self.update_user_attribute('set_num_frames',l))
        #cv2.createTrackbar('segments', 'anpassen', 1, 130,
        #        lambda l: self.update_user_attribute('set_num_segments',l))

        if DEBUG:
            flags = cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO 
        else:
            flags = cv2.WINDOW_NORMAL
        cv2.namedWindow("installation", flags)

        if not DEBUG:         
            cv2.setWindowProperty("installation", cv2.WND_PROP_FULLSCREEN,
                                    cv2.WINDOW_FULLSCREEN)
    
    
    def get_frame(self):
        """ get current frame from active video device """
        ret, frame1 = self._cap.read()
        # if cam device is not ready, retry
        while(not ret):
            ret, frame1 = self._cap.read()
        # mirror image horizontaly
        frame1 = cv2.flip(frame1, 1) 

        return frame1
    
      
    def save_frame(self):
        """ save current frame """ 
        imgName = '%s.png'%(self._current_user.get_save_fn())
        cv2.imwrite(imgName, self.current_frame)
        print "img saved:", imgName 
     
     
    def start_video(self, name):
        """ start saving a video with the given name """
        vidName = '%s.avi'%(self._current_user.get_save_fn())
        # video recorder
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #if DEBUG:
            #popup dialog with codec list
        fourcc = -1
        self._video = cv2.VideoWriter(vidName,fourcc,5.0,(self.window_width, self.window_height))
    
    
    def stop_video(self):
        """ stop the video, release the memory """
        self._video.release()
        self._video = None
    
    def create_frame(self, frames, live_frame=None):
        """ set current frame from combined 3 snippets and one live frame  """
        # frames - array of frame fragments with same vert/horizontal dimensions
        canvas = np.zeros((self.window_height, self.window_width,3),np.uint8)
        if frames:
            frameTmp = np.vstack(frames)
            #frameTmp = cv2.resize(frameTmp, (self.window_width, self.window_height))
            frame_width = frameTmp.shape[1]
            frame_height= frameTmp.shape[0]
            alpha = 0.0
            canvas[:frame_height,:frame_width] = cv2.addWeighted(canvas[:frame_height,:frame_width],
                                                                   alpha, frameTmp, 1.0 - alpha,0.0)
        if live_frame is not None:
            smallSize = (int(self.window_width*0.2), int(self.window_height*0.2))
            smallLive = cv2.resize(live_frame, smallSize)
            alpha = 0.1
            canvas[-smallSize[1]:,-smallSize[0]:] = cv2.addWeighted(canvas[-smallSize[1]:,-smallSize[0]:] ,
                                                                    alpha, smallLive, 1.0 - alpha,0.0)
        return canvas

    
    
    def quit(self, terminate=False):
        """ if terminate set is_runnig flag to false, clear up memory """
        self.RUN_USER = False
        if self._video:
            self.stop__video()
        if terminate:
            self.is_running = False
            # When everything done, release all ressources
            self._cap.release()
            cv2.destroyAllWindows()

              
    def process_key(self, key):
        """ handle input key pressed """
        # ignore nonascii input
        key = key & 0xFF
        if key > 254:
            return
        if self._gui:
            if self._gui.process_key(key):
                return
        if key == ord('s'):
            self.save_frame()
        elif key == ord('q'):
            print "quit"
            self.quit(True)
        elif key == ord('m'):
            print "change user mode to multi stripes"
            self.user_mode = False
        elif key == ord('d'):
            print "change user mode to face detect"
            self.user_mode = True       
        elif key == ord('c'):
            print "changing user"
            self.quit()
        elif key == ord('v'):         
            if self._video:
                self.stop_video()
                print "_video saved : ", self._current_user.name
            else:
                self.start_video(self._current_user.name)
                print "saving _video : ", self._current_user.name
    
    
    def set_username(self, name):
        """ set the name to the current user, make dir for the user, if not there """
        self._current_user.name = name
        print "new User Object: ", name
        if not os.path.exists("../%s"%name):
            os.makedirs("../%s"%name)
            print "new folder for user:", name 
        # all done disable user GUI
        self._gui = None
    
 
    def create_user(self):
        """ make new user object according to the current mode """
        if self.user_mode:
            user = FaceDetectionUser()
            print "face detect user mode"
        else:
            user = MultiStripesUser(segments=3)
            print "multi stripes user mode"
        if DEBUG:
            user.name = 'debug' 
        #else:
        #    self._gui = UserInputGUI("Ihr Name?", self.set_username)
        self._current_user = user
        self.RUN_USER = True
           
       
    def run_session(self):
        """ main logic loop """  
        starttime = 0.0
        while(self.RUN_USER):
            start2 = time()
            frame = self.get_frame()
            etime = time() - starttime  
            
            if etime > self._speed:            
                starttime = time()
                self._current_user.cut_frame_to_segments(frame)
                frames = self._current_user.get_segment_list()


            self.current_frame = self.create_frame(frames, frame)

            if self._gui:
                self._gui.draw(self.current_frame)
                
            cv2.imshow('installation', self.current_frame)
            
            if self._video:
                self._video.write(self.current_frame)
           
            # synchronize the data with OpenCV 
            key = cv2.waitKey(1)
            self.process_key(key)
