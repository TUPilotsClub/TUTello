from pygame import constants
from .guicomponent import GUIComponent
from video.videofeed import VideoFeed
import pygame
import cv2
import numpy as np
from typing import Text, Tuple

class TextComponent(GUIComponent):
    DEFAULT_FONT_SIZE = 25
    DEFAULT_FONT = "Arial"

    def __init__(self, format_string: str, position: Tuple[int, int], color: Tuple[int, int, int]=(0,0,255), 
                size: int=None, font: str=None, is_constant: bool=True):
        if size is None:
            size = TextComponent.DEFAULT_FONT_SIZE
        if font is None:
            font = TextComponent.DEFAULT_FONT

        self.format_string = format_string
        self.position = position
        self.size = size
        self.font = font
        self.color = color
        self.is_constant = is_constant
        self.variables = {}

    def setVariables(self, variables: dict):
        if (self.is_constant):
            raise RuntimeError('Cannot set variables for constant TextComponent')
        self.variables = variables

    def setKeyValue(self, key, value):
        if (self.is_constant):
            raise RuntimeError('Cannot set variable for constant TextComponent')
        self.variables[key] = value

    def get_surface(self):
        if (not self.is_constant and not self.variables):
            raise RuntimeError('Cannot get formatted text without initialized variables')
        if (not self.pygame_font):
            raise RuntimeError('TextComponent has not been initialized')
        if (self.is_constant):
            text = self.format_string
        else:
            text = self.format_string.format(**self.variables)
        return self.pygame_font.render(text, True, self.color)
        
    def get_position(self):
        return self.position

    def initialize(self):
        self.pygame_font = pygame.font.SysFont(self.font, self.size)