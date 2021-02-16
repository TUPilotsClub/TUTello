from djitellopy.tello import Tello

class VideoFeed:
    def __init__(self, tello):
        if not isinstance(tello, Tello):
            raise TypeError("Parameter 'tello' should be of type Tello")
            
        self.tello = tello
        self.frame_read = None
        
    def get_frame(self):
        if not self.frame_read:
            self.frame_read = self.tello.get_frame_read()
        return self.frame_read.frame
        
    def enable_video(self):
        if not self.tello.streamon():
            print("Could not start video stream")
            return
            
    def disable_video(self):
        if not self.tello.streamoff():
            print("Could not stop video stream")
            return