from djitellopy.tello import Tello
import matplotlib.pyplot as plt
from .videofeed import VideoFeed
import cv2
import numpy as np

class RedBallVideo(VideoFeed):
    def __init__(self, tello):
        if not isinstance(tello, Tello):
            raise TypeError("Parameter 'tello' should be of type Tello")
        self.img = plt.imread("../compvis_L1/redball1.jpeg")
        """ self.redFilter()
        self.blobFinder() """
        #self.img = self.img[..., ::-1]
        self.counter = 0
        self.hue = 155


        self.tello = tello
        self.frame_read = None
        
    def get_frame(self):
        if not self.frame_read:
            self.frame_read = self.tello.get_frame_read()
        # return self.frame_read.frame
        self.img = self.frame_read.frame
        self.redFilter()
        self.blobFinder()

        self.counter += 1
        tmp = (self.counter//25)%3
        if tmp == 0:
            return cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        elif tmp == 1:
            #self.hue = (self.hue + 1) % 170
            return self.mask
        elif tmp == 2:
            return self.filtered
        raise ValueError("Counter isn't correct")
    
    def enable_video(self):
        if not self.tello.streamon():
            print("Could not start video stream")
        return
            
    def disable_video(self):
        if not self.tello.streamoff():
            print("Could not stop video stream")
        return
    
    def redFilter(self):
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        
        lower_red = np.array([self.hue,25,25])
        upper_red = np.array([self.hue + 25,255,255])
        print(self.hue)

        self.mask = cv2.inRange(hsv, lower_red, upper_red)
        self.res = cv2.bitwise_and(self.img, self.img, mask= self.mask)

    def blobFinder(self):

        params = cv2.SimpleBlobDetector_Params()

        params.minThreshold = 100
        params.maxThreshold = 200

        # Set up the detector with default parameters.
        detector = cv2.SimpleBlobDetector_create(params)
        # Detect blobs.
        keypoints = detector.detect(self.mask)
        # Draw detected blobs as red circles.
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
        self.filtered = cv2.drawKeypoints(self.img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)