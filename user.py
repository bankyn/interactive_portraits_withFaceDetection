"""
    user classes, implements 
"""

import random
import cv2

from face_utils import find_faces

class User(object):
    """ generic class for user objects """
    def __init__(self, segments=3, segment_list_length=10):
        self.name= ""
        self.imgNr = 0
        self.num_segments = segments
        self.segment_list_length = segment_list_length
        self.segments = [[] for i in range(segments)]
        self.midEyeY = 100
        self.noseY = 200
        print('ll=',self.segment_list_length)
    
 
    def get_save_fn(self):
        imgName = '../%s/%s_%d'%(self.name, self.name, self.imgNr)
        self.imgNr += 1
        return imgName
    
    def _add_segment(self, segment_index, segment):
        """ implements simple fifo for each segment list """
        if len(self.segments[segment_index]) >= self.segment_list_length:
           del self.segments[segment_index][0]
           print(self.segment_list_length)
        self.segments[segment_index].append(segment)

    def set_num_frames(self, num):
        """ callback for the frame number trackbar """
        if num > 0:
            self.segment_list_length = num
            # delete rest frames in each segment list if more than num_frames
            for seg_idx in range(self.num_segments):
                while(len(self.segments[seg_idx]) >= self.segment_list_length):
                    del self.segments[seg_idx][0]


    def set_num_segments(self, num):
        """ callback for the segment number trackbar """
        if num > 0:
            self.num_segments = num
            # reinitialize segment lists
            self.segments = [[] for i in range(num)]


class MultiStripesUser(User):
    """ derived user class for splitting in num_segment equal segments """
    def cut_frame_to_segments(self, frame):
        """ splits the current frame in segments"""
        y0 = 0
        dy = frame.shape[0] / (self.num_segments-1)
        for idx in range(self.num_segments-1):
            y = y0 +dy
            seg = frame[y0:y]
            self._add_segment(idx, seg)
            y0 = y 
        idx +=1
        seg = frame[y0:]
        self._add_segment(idx, seg)

    def get_segment_list(self, delta=5, alpha=0.8):
        """ returns list of a random frame per segment """
        frames = []
        for segment_idx in range(self.num_segments):
            idx0 = random.randint(0,len(self.segments[0])-1)
            frames.append(self.segments[segment_idx][idx0])
        return frames
    
class FaceDetectionUser(User):
    """ derived user class for splitting the frame in eye, nose and mouth segments """
    def __init__(self, num_frames=25*10):
        super(FaceDetectionUser, self).__init__(3, num_frames)
        self.midEyeY = 100
        self.noseY = 200
        self.width = 1920 /3
        self.index = 0
    def set_num_segments(self, num):
        #not supported yet? fail silently
        pass

    
    def cut_frame_to_segments(self, frame):
        """ split frame in eye, nose and mouth segments """
        faces_coordinates_list = find_faces(frame)
        for face_coordinates in faces_coordinates_list:
            self.midEyeY = face_coordinates[0]
            self.noseY = face_coordinates[1]
            frame_face = face_coordinates[2]
            eye_segment = frame_face[0:self.midEyeY]
            nose_segment = frame_face[self.midEyeY:self.midEyeY+self.noseY]
            mouth_segment = frame_face[self.midEyeY+self.noseY:-1]
            height = int(self.width*eye_segment.shape[0] / eye_segment.shape[1]) # h/w
            eye_segment = cv2.resize(eye_segment, (self.width, height))
            height = int(self.width*nose_segment.shape[0] / nose_segment.shape[1]) # h/w
            nose_segment = cv2.resize(nose_segment, (self.width, height))
            height = int(self.width*mouth_segment.shape[0] / mouth_segment.shape[1]) # h/w

            mouth_segment = cv2.resize(mouth_segment, (self.width, height))

            self._add_segment(0, eye_segment)
            self._add_segment(1, nose_segment)
            self._add_segment(2, mouth_segment)


    def get_segment_list(self, delta=5, alpha=0.8):
        """ returns list of random frame per segment
            with the overlay strength of alpha and height of delta
        """
        # get random segments
        if len(self.segments[0]) < 100 :
            return None

        self.index +=1
        idx0 = 0
        idx1 = 0
        idx2 = 0
        #ein bisschen komisches wechseln nacheinander, aber sieht schon lustig aus:
        if self.index >= len(self.segments[0]):
            idx0 = len(self.segments[0]) - random.randint(1,10)*10
            if self.index -len(self.segments[0]) >= len(self.segments[1]):
                idx1 = len(self.segments[1]) -random.randint(1,10)*10  #change freeze frame!
                if self.index -len(self.segments[0]) - len(self.segments[1]) >=  len(self.segments[2]):
                    idx2 = len(self.segments[2]) -random.randint(1,10)*10
                    self.index = 0
                else:
                    idx2 = self.index -len(self.segments[0]) -len(self.segments[1])
            else:
                idx1 = self.index -len(self.segments[0])

        else:
            idx0 = self.index -1
        # get, blend and return the segments
        fr0 = self.segments[0][idx0]
        fr0b = self.segments[0][idx1]
        fr0[-delta:] = cv2.addWeighted(fr0[-delta:],alpha,fr0b[-delta:],1.0 - alpha,0.0)       
        fr1 = self.segments[1][idx1]
        fr1b = self.segments[1][idx0]
        fr1c = self.segments[1][idx2]
        fr1[:delta] = cv2.addWeighted(fr1[:delta],alpha,fr1b[:delta],1.0 - alpha,0.0)
        fr1[-delta:] = cv2.addWeighted(fr1[-delta:],alpha,fr1c[-delta:],1.0 - alpha,0.0)
        fr2 = self.segments[2][idx2]
        fr2b = self.segments[2][idx1]
        fr2[:delta] = cv2.addWeighted(fr2[:delta],alpha,fr2b[:delta],1.0 - alpha,0.0)
        
        return [fr0,fr1,fr2]
