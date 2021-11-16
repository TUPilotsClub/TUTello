from gui.pyevents import PyEvents
from gui.simplegui import SimpleGUI
from .controller import Controller
from drone import Tello
import pygame
import threading
import time

class SimpleController(Controller):
    UP_DIR = "up"
    DOWN_DIR = "down"
    LEFT_DIR = "left"
    RIGHT_DIR = "right"
    W_DIR = "w"
    S_DIR = "s"
    A_DIR = "a"
    D_DIR = "d"

    def __init__(self, tello: Tello, gui: PyEvents):
        super(SimpleController, self).__init__(tello)
        
        self.speed = 50
        self.send_rc_control = False

        self.keys = {
            self.UP_DIR: False,
            self.DOWN_DIR: False,
            self.LEFT_DIR: False,
            self.RIGHT_DIR: False,
            self.W_DIR: False,
            self.S_DIR: False,
            self.A_DIR: False,
            self.D_DIR: False
        }
        
        gui.subscribe_keydown(self.pitchEvents(self.UP_DIR, True), pygame.K_UP)
        gui.subscribe_keydown(self.pitchEvents(self.DOWN_DIR, True), pygame.K_DOWN)
        gui.subscribe_keydown(self.rollEvents(self.RIGHT_DIR, True), pygame.K_RIGHT)
        gui.subscribe_keydown(self.rollEvents(self.LEFT_DIR, True), pygame.K_LEFT)
        gui.subscribe_keydown(self.thrustEvents(self.W_DIR, True), pygame.K_w)
        gui.subscribe_keydown(self.thrustEvents(self.S_DIR, True), pygame.K_s)
        gui.subscribe_keydown(self.yawEvents(self.A_DIR, True), pygame.K_a)
        gui.subscribe_keydown(self.yawEvents(self.D_DIR, True), pygame.K_d)
        
        gui.subscribe_keyup(self.pitchEvents(self.UP_DIR, False), pygame.K_UP)
        gui.subscribe_keyup(self.pitchEvents(self.DOWN_DIR, False), pygame.K_DOWN)
        gui.subscribe_keyup(self.rollEvents(self.RIGHT_DIR, False), pygame.K_RIGHT)
        gui.subscribe_keyup(self.rollEvents(self.LEFT_DIR, False), pygame.K_LEFT)
        gui.subscribe_keyup(self.thrustEvents(self.W_DIR, False), pygame.K_w)
        gui.subscribe_keyup(self.thrustEvents(self.S_DIR, False), pygame.K_s)
        gui.subscribe_keyup(self.yawEvents(self.A_DIR, False), pygame.K_a)
        gui.subscribe_keyup(self.yawEvents(self.D_DIR, False), pygame.K_d)
        
        gui.subscribe_keyup(self.takeoff, pygame.K_t)
        gui.subscribe_keyup(self.land, pygame.K_l)
        
        gui.subscribe_destructor(self.destruct)
        
        # update_thread = threading.Thread(target=self.update, args=())
        # update_thread.Daemon = True
        # update_thread.start()
        
    def pitchEvents(self, key, val):
        def eventFunc():
            self.keys[key] = val
            self.setPitch((self.keys[self.UP_DIR] - self.keys[self.DOWN_DIR]) * self.speed)
        return eventFunc

    def rollEvents(self, key, val):
        def eventFunc():
            self.keys[key] = val
            self.setRoll((self.keys[self.RIGHT_DIR] - self.keys[self.LEFT_DIR]) * self.speed)
        return eventFunc

    def thrustEvents(self, key, val):
        def eventFunc():
            self.keys[key] = val
            self.setThrust((self.keys[self.W_DIR] - self.keys[self.S_DIR]) * self.speed)
        return eventFunc

    def yawEvents(self, key, val):
        def eventFunc():
            self.keys[key] = val
            self.setYaw((self.keys[self.D_DIR] - self.keys[self.A_DIR]) * self.speed)
        return eventFunc