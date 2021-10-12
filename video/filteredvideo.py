from typing import Callable, List
from drone.tello import Tello
import cv2
from video.videofeed import VideoFeed

class FilteredVideo(VideoFeed):
    def __init__(self, tello: Tello): 
        super().__init__(tello)

        self.filters = []

    def get_frame(self):
        img = super().get_frame()

        for filter in self.filters:
            img = filter(img)

        return img

    def then(self, filter: Callable):
        self.filters.append(filter)
        #return self to enable this syntax: fv.then(func1).then(func2)
        return self