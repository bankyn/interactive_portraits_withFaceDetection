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
from face_utils import find_faces
import random
import string

class Instance(object):
    def __init__(self):
        self.is_running = True
        self._cap = None
        self.window_height = 1080
        self.window_width = 1920
        # 1 fps initially
        self._speed = 1/25.0
        self._video = None
        self._gui = UserInputGUI()
        self._current_users = []
        self._old_users = []
        self.current_frame = None
        self.user_mode = True
        self.show_live = True
        self.RUN_USER = True
        self.user = None
        self.second_users = None

        self.init(VIDEO_DEVICE)
        self.index = [0,0,0]
        self.live_segment = 0

        # Do not record on default.
        self.video_stream = None
        self.record = False

    def capture_video(self, frame):

        canvas = np.zeros(shape=(800,640,3), dtype=frame.dtype)
        if self.video_stream is None:
            fourcc = -1
            filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3))
            filename += ".avi"
            self.video_stream = cv2.VideoWriter(filename, fourcc, 20.0, (canvas.shape[1], canvas.shape[0]))

        dh = (canvas.shape[0] - frame.shape[0])/2
        canvas[dh:dh + frame.shape[0]] = frame
        self.video_stream.write(canvas)


    def set_fps(self, fps):
        """ callback for the fps trackbar """
        if fps <= 0:
            return
        self._speed = 1.0/fps
        
    def update_user_attribute(self, fn, value):
        if len(self._current_user) == 0:
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

        #if DEBUG:
        #    flags = cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO
        #else:
        flags = cv2.WINDOW_NORMAL
        cv2.namedWindow("installation", flags)

        #if not DEBUG:
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

    def draw_segments(self, frameTmp, pos=(0,0)):
        """ set current frame from combined 3 snippets and one live frame  """
        # frames - array of frame fragments with same vert/horizontal dimensions
        #frameTmp = np.vstack(segment_list)
        #frameTmp = cv2.resize(frameTmp, (self.window_width, self.window_height))
        frame_width = frameTmp.shape[1] + pos[0]
        frame_height= frameTmp.shape[0] + pos[1]
        alpha = 0.0
        if frame_height > 1000:
            frameTmp = frameTmp[:1000-pos[1]]
            frame_height = 1000
        self.current_frame[pos[1]:frame_height,pos[0]:frame_width] = cv2.addWeighted(
            self.current_frame[pos[1]:frame_height,pos[0]:frame_width],
            alpha, frameTmp, 1.0 - alpha,0.0)

    def quit(self, terminate=False):
        """ if terminate set is_runnig flag to false, clear up memory """
        self.RUN_USER = False
        if self.video_stream:
            self.video_stream.release()
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
        #if self._gui:
        #    if self._gui.process_key(key):
        #        return
        if key == ord('q'):
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
        elif key == ord('r'):
            print "Toggl record"
            if self.video_stream:
                self.video_stream.release()
                self.video_stream = None
            self.record = not self.record

    def create_user(self, current_pos=None):
        """ make new user object according to the current mode """
        if self.user_mode:
            user = FaceDetectionUser(current_pos=current_pos)
            print "face detect user mode"
        else:
            user = MultiStripesUser(segments=3)
            print "multi stripes user mode"
        if DEBUG:
            user.name = 'debug' 
        self._current_users.append(user)
        self.RUN_USER = True
        return user
        
    def switch_logic(self):
        self.index[self.live_segment] += 1
        if self.index[self.live_segment] > 5*25:# \
            #or self.index[self.live_segment] > len(self.user.segments[self.live_segment])+5:
            self.index[self.live_segment] = None
            self.live_segment += 1
            self.live_segment = self.live_segment % 3
            if self.index[self.live_segment] is None:
                self.index[self.live_segment] = 0

            self._gui.switch_text(self.live_segment)

        # and switch the user
        if len(self._current_users):
            self.user = random.choice(self._current_users)
        #elif len(self._old_users):
        #    self.user = random.choice(self._old_users)
        else:  # do not switch
            self.user = None
        if len(self._old_users):
            self.second_users = [random.choice(self._old_users + self._current_users),
                             random.choice(self._old_users + self._current_users),
                             random.choice(self._old_users + self._current_users)]
       
    def run_session(self):
        """ main logic loop """  
        starttime = 0.0

        while(self.RUN_USER):
            start2 = time()
            frame = self.get_frame()

            etime = start2 - starttime

            if etime > self._speed:
                #print(1.0/etime)
                starttime = start2
                faces = find_faces(frame)
                for face in faces:
                    no_match = True
                    for user in self._current_users:
                        distance = np.linalg.norm(user.current_position - face[3])
                        #print(distance)
                        if distance < 50.0:
                            user.cut_frame_to_segments(face)
                            user.age = 0
                            no_match = False
                            break
                    if no_match:
                        print("create user")
                        user = self.create_user(face[3])
                        user.cut_frame_to_segments(face)

                        #switch to the new user
                        self.user = user
                #choose three random users and get a segment from each
                #but first try to place them next to each other!
                self.current_frame = np.zeros((self.window_height, self.window_width,3),np.uint8)

                for user in self._current_users:
                    user.age += 1
                    #frames = user.get_segment_list()
                    #if frames:
                        #pos = user.current_position.copy()
                        #pos[0] *= 4.
                    if user.age > 2:
                        self._current_users.remove(user)
                    if len(user.segments[0]) > 20:
                        self._old_users.append(user)
                        self._current_users.remove(user)
                        
                        
                    if len(self._old_users) > 100:
                            del self._old_users[0]
                            print("delte one old user. limit 100")

                self.switch_logic()
                if self.user:
                    text = "Rec {0} users - age={1} t={2}  ".format(len(self._current_users),
                                                self.user.age, len(user.segments[0]))
                else:
                    text = "{1} / {0}".format(len(self._old_users), len(self._current_users))

                self._gui.debug_text = text
                if self.user:
                    t,m,b = self.index
                    self.draw_segments(np.vstack([
                        self.user.get_segment(0,t),
                        self.user.get_segment(1,m),
                        self.user.get_segment(2,b)
                    ]),pos=(50,200))

                if self.second_users:
                    alle = self.index[self.live_segment]
                    frame = np.vstack([
                        self.second_users[0].get_segment(0,alle),
                        self.second_users[1].get_segment(1,alle),
                        self.second_users[2].get_segment(2,alle)
                    ])
                    self.draw_segments(frame, pos=(1230,200))
                    if self.record:
                        self.capture_video(frame)


            if DEBUG:
                smallSize = (int(self.window_width*0.2), int(self.window_height*0.2))
                smallLive = cv2.resize(frame, smallSize)
                alpha = 0.1
                self.current_frame[-smallSize[1]:,-smallSize[0]:] = cv2.addWeighted(
                    self.current_frame[-smallSize[1]:,-smallSize[0]:],
                    alpha, smallLive, 1.0 - alpha,0.0)

            if self._gui:
                self._gui.draw(self.current_frame)
                
            cv2.imshow('installation', self.current_frame)
            
            if self._video:
                self._video.write(self.current_frame)
           
            # synchronize the data with OpenCV 
            key = cv2.waitKey(1)
            self.process_key(key)
