from typing import Iterable
from drone.tello import Tello
from video.videofeed import VideoFeed
from .pyevents import PyEvents
from .guicomponent import GUIComponent
from collections import defaultdict
import cv2
import pygame
import numpy as np
import time
import sys

class GUI(PyEvents):
    """Coordinates events and displays Tello video and states"""
    
    # Frames per second of the pygame window display
    FPS = 25

    def __init__(self, components: Iterable[GUIComponent]):
        if not components:
            components = []
        if not components.__iter__:
            raise TypeError("Parameter 'components' should be of type Iterable[GUIComponent]")
        
        # Init pygame
        pygame.init()
        
        # Create pygame window
        pygame.display.set_caption("TUTello")
        self.screen = pygame.display.set_mode([960, 720])
        self.background_color = [0, 0, 0]
        
        self.components = components
        
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
            print(self.components)
            for comp in self.components:
                comp.initialize()

            should_stop = False
            while not should_stop:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        should_stop = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            should_stop = True
                            continue
                        self.keydown(event.key)
                    elif event.type == pygame.KEYUP:
                        self.keyup(event.key)
                
                #set background
                self.screen.fill(self.background_color)
                
                for comp in self.components:
                    pos = comp.get_position()
                    surface = comp.get_surface()
                    if pos and surface:
                        self.screen.blit(surface, pos)
                pygame.display.update()

                time.sleep(1 / self.FPS)
        except:
            print("Unexpected error:", sys.exc_info())
            
        print("terminated")
        try:
            # Call it always before finishing. To deallocate resources.
            for func in self.destructor_subs:
                try:
                    func()
                except:
                    print("func couldn't terminate", func)
        except:
            print("Unexpected error:", sys.exc_info())
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