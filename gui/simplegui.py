from djitellopy.tello import Tello
from .videofeed import VideoFeed
from .pyevents import PyEvents
from collections import defaultdict
import cv2
import pygame
import numpy as np
import time
import sys

class SimpleGUI(PyEvents):
    """Coordinates events and displays Tello video and states"""
    
    # Frames per second of the pygame window display
    FPS = 25

    def __init__(self, videofeed):
        if not isinstance(videofeed, VideoFeed):
            raise TypeError("Parameter 'videofeed' should be of type VideoFeed")
        # Init pygame
        pygame.init()
        
        # Create pygame window
        pygame.display.set_caption("TUTello")
        self.screen = pygame.display.set_mode([960, 720])
        self.videofeed = videofeed
        
        self.keydown_subs = defaultdict(list)
        self.keyup_subs = defaultdict(list)
        self.destructor_subs = [self.exit_pygame]        
        
    def subscribe_keydown(self, func, key):
        self.keydown_subs[key].append(func)
        
    def subscribe_keyup(self, func, key):
        self.keyup_subs[key].append(func)
        
    def subscribe_destructor(self, func):
        self.destructor_subs.append(func)

    def run(self):
        try:
            self.videofeed.disable_video()
            self.videofeed.enable_video()

            should_stop = False
            while not should_stop:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        should_stop = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            should_stop = True
                        else:
                            self.keydown(event.key)
                    elif event.type == pygame.KEYUP:
                        self.keyup(event.key)
                
                #black background
                self.screen.fill([0, 0, 0])
                #get frame
                frame = self.videofeed.get_frame()
                if not frame is None:
                    #transform to screen format
                    frame = np.rot90(frame)
                    frame = np.flipud(frame)
                    frame = pygame.surfarray.make_surface(frame)
                    self.screen.blit(frame, (0, 0))
                pygame.display.update()

                time.sleep(1 / self.FPS)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            
        print("terminated")
        try:
            # Call it always before finishing. To deallocate resources.
            for func in self.destructor_subs:
                func()
        except:
            print("Unexpected error:", sys.exc_info()[0])
            sys.exit(1)

    def keydown(self, key):
        subs = self.keydown_subs[key]
        for func in subs:
            func()
            
    def keyup(self, key):
        subs = self.keyup_subs[key]
        for func in subs:
            func()
            
    def exit_pygame(self):
        pygame.display.quit()
        pygame.quit()