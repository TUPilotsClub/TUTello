from .guicomponent import GUIComponent
from video.videofeed import VideoFeed
import pygame
import cv2
import numpy as np
from typing import Tuple

class VideoComponent(GUIComponent):
    def __init__(self, videofeed: VideoFeed, position: Tuple[int, int]=(0,0)):
        self.videofeed = videofeed
        self.position = position

    def get_surface(self):
        frame = self.videofeed.get_frame()
        if frame is None:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        #transform to screen format
        frame = np.rot90(frame)
        frame = np.flipud(frame)
        surface = pygame.surfarray.make_surface(frame)
        return surface
        
    def get_position(self):
        return self.position

    def initialize(self):
        #to fix a weird tello bug
        self.videofeed.disable_video()
        self.videofeed.enable_video()