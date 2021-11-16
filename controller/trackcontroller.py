from controller.tracktelemetry import TrackTelemetry
from gui.pyevents import PyEvents
from gui.simplegui import SimpleGUI
from .controller import Controller
from drone import Tello
import pygame
import threading
import time

class TrackController(Controller):

    def __init__(self, tello: Tello, gui: PyEvents, telemetry: TrackTelemetry):
        super(TrackController, self).__init__(tello)
        
        self.update_func = self.track_move
        
        self.speed = 50
        self.send_rc_control = False

        self.telemetry = telemetry
        
        if tello != None:
            gui.subscribe_keyup(self.takeoff, pygame.K_t)
            gui.subscribe_keyup(self.land, pygame.K_l)
        
        gui.subscribe_destructor(self.destruct)
        
        # update_thread = threading.Thread(target=self.update, args=())
        # update_thread.Daemon = True
        # update_thread.start()


    def track_move(self):
        print("tracking", int(self.telemetry.target[0] * self.speed))
        #self.setYaw(int(self.telemetry.target[1] * self.speed))
        self.setYaw(int(self.telemetry.target[0] * self.speed))