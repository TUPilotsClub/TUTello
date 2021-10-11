from drone.tello import Tello
import matplotlib.pyplot as plt
from .videofeed import VideoFeed
import cv2
import imutils
import numpy as np
import os

class FaceTrackVideo(VideoFeed):
    def __init__(self, tello: Tello):
        super().__init__(tello)

    def get_frame(self):
        img = super().get_frame()
        if img is None:
            raise ValueError("frame not found")
        rect_img, bounds = self.find_face(img)
        return rect_img

    def find_face(self, img):
        faceCascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml'))
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(imgGray, 1.1, 6)

        myFaceListC = []
        myFaceListArea = []

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cx = x + w // 2
            cy = y + h // 2
            area = w * h
            myFaceListArea.append(area)
            myFaceListC.append([cx, cy])

        if len(myFaceListArea) != 0:
            i = myFaceListArea.index(max(myFaceListArea))
            return img, [myFaceListC[i], myFaceListArea[i]]
        else:
            return img, [[0, 0], 0]