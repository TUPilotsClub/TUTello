from controller.tracktelemetry import TrackTelemetry
from drone.tello import Tello
import matplotlib.pyplot as plt
from .videofeed import VideoFeed
import cv2
import imutils
import numpy as np

class RedBallVideo(VideoFeed):
    def __init__(self, tello: Tello, telemetry: TrackTelemetry):
        super().__init__(tello)
            
        self.counter = 0
        self.frame_read = None
        self.telemetry = telemetry
            
    def get_frame(self):
        self.img = super().get_frame()
        self.redFilter()
        #self.blobFinder()
        self.contourFinder()

        self.counter += 1
        tmp = (self.counter//25)%3
        if tmp == 0:
            return self.filtered
        elif tmp == 1:
            #self.hue = (self.hue + 1) % 170
            return self.mask
        elif tmp == 2:
            return self.filtered
        raise ValueError("Counter isn't correct")
    
    def redFilter(self):
        hue = 170
        hueRange = 20
        minSat = 110
        minBright = 110
        #self.img[:] = (0,0,255)
        blur = cv2.GaussianBlur(self.img, (5, 5), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        lower_red = np.array([hue,minSat,minBright])
        upper_red = np.array([min(hue+hueRange,179),255,255])
        self.mask = cv2.inRange(hsv, lower_red, upper_red)
        
        if hue + hueRange >= 180:
            lower_red = np.array([0,minSat,minBright])
            upper_red = np.array([(hue+hueRange)%180,255,255])
            mask2 = cv2.inRange(hsv, lower_red, upper_red)
            self.mask = cv2.bitwise_or(self.mask, mask2)
            
        self.mask = cv2.erode(self.mask, np.ones((3,3)))
        self.mask = cv2.dilate(self.mask, np.ones((9,9)))
        self.res = cv2.bitwise_and(self.img, self.img, mask= self.mask)

    def blobFinder(self):

        params = cv2.SimpleBlobDetector_Params()

        params.minThreshold = 70
        params.maxThreshold = 300
        params.filterByCircularity = False
       

        # Set up the detector with default parameters.
        detector = cv2.SimpleBlobDetector_create(params)
        # Detect blobs.
        keypoints = detector.detect(self.mask)
        # Draw detected blobs as red circles.
        # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
        self.filtered = cv2.drawKeypoints(self.img, keypoints, np.array([]), (0,255,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        
        
    def contourFinder(self):
        cnts = cv2.findContours(self.mask, cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        
        
        #self.filtered = cv2.morphologyEx(self.mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (151,151)));
        self.filtered = self.img
        if (cnts is None or len(cnts) == 0):
            return
                       
        c = max(cnts, key = cv2.contourArea)
        
        if cv2.contourArea(c) < 10:
            return
        # compute the center of the contour
        M = cv2.moments(c)
        if M["m00"] == 0:
            self.telemetry.target = (0,0)
            return
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        # draw the contour and center of the shape on the image
        cv2.drawContours(self.filtered, [c], -1, (0, 255, 0), 2)
        cv2.circle(self.filtered, (cX, cY), 7, (255, 255, 255), -1)
        cv2.putText(self.filtered, "center", (cX - 20, cY - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        self.telemetry.target = (cX / self.img.shape[1] - 0.5)*2, (cY / self.img.shape[0] - 0.5)*2