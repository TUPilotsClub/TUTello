from drone.tello import Tello
import cv2

class VideoFeed:
    def __init__(self, tello: Tello):            
        self.tello = tello
        self.frame_read = None
        
        self.webcamCapture = cv2.VideoCapture(0)

    def get_frame(self):
        if self.tello:
            if not self.frame_read:
                self.frame_read = self.tello.get_frame_read()
            return self.frame_read.frame
        else:
            _, frame = self.webcamCapture.read()
            return frame
        
    def enable_video(self):
        if self.tello and not self.tello.streamon():
            print("Could not start video stream")
            return
            
    def disable_video(self):
        if self.tello and not self.tello.streamoff():
            print("Could not stop video stream")
            return