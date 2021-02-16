from gui.pyevents import PyEvents
import pygame
import threading
import time

class SimpleController:
    # Speed of the drone
    S = 60
    
    def __init__(self, tello, gui):
        if not isinstance(gui, PyEvents):
            raise TypeError("Parameter 'gui' should be of type SimpleGUI")
            
        self.tello = tello
        
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10
        self.send_rc_control = False
        
        gui.subscribe_keydown(self.forward, pygame.K_UP)
        gui.subscribe_keydown(self.backward, pygame.K_DOWN)
        gui.subscribe_keydown(self.right, pygame.K_RIGHT)
        gui.subscribe_keydown(self.left, pygame.K_LEFT)
        gui.subscribe_keydown(self.yaw_clck, pygame.K_d)
        gui.subscribe_keydown(self.yaw_count_clck, pygame.K_a)
        gui.subscribe_keydown(self.upward, pygame.K_w)
        gui.subscribe_keydown(self.downward, pygame.K_s)
        
        gui.subscribe_keyup(self.forward, pygame.K_DOWN)
        gui.subscribe_keyup(self.backward, pygame.K_UP)
        gui.subscribe_keyup(self.right, pygame.K_LEFT)
        gui.subscribe_keyup(self.left, pygame.K_RIGHT)
        gui.subscribe_keyup(self.yaw_clck, pygame.K_a)
        gui.subscribe_keyup(self.yaw_count_clck, pygame.K_d)
        gui.subscribe_keyup(self.upward, pygame.K_s)
        gui.subscribe_keyup(self.downward, pygame.K_w)
        
        gui.subscribe_keyup(self.takeoff, pygame.K_t)
        gui.subscribe_keyup(self.land, pygame.K_l)
        
        gui.subscribe_destructor(self.destruct)
        
        update_thread = threading.Thread(target=self.update, args=())
        update_thread.Daemon = True
        update_thread.start()
        
            
    def forward(self):
        if self.for_back_velocity > 0:
            return
        self.for_back_velocity += self.S
            
    def backward(self):
        if self.for_back_velocity < 0:
            return
        self.for_back_velocity -= self.S
        
    def right(self):
        if self.left_right_velocity > 0:
            return
        self.left_right_velocity += self.S
        
    def left(self):
        if self.left_right_velocity > 0:
            return
        self.left_right_velocity -= self.S
        
    def yaw_clck(self):
        if self.yaw_velocity > 0:
            return
        self.yaw_velocity += self.S
        
    def yaw_count_clck(self):
        if self.yaw_velocity < 0:
            return
        self.yaw_velocity -= self.S
        
    def upward(self):
        if self.up_down_velocity > 0:
            return
        self.up_down_velocity += self.S
        
    def downward(self):
        if self.up_down_velocity < 0:
            return
        self.up_down_velocity -= self.S
        
    def takeoff(self):
        print("takeoff")
        self.tello.takeoff()
        self.send_rc_control = True
        
    def land(self):
        print("land")
        self.tello.land()
        self.send_rc_control = False
        
    def destruct(self):
        self.tello.end()
        
    def update(self):
        """ Update routine. Send velocities to Tello."""
        while (True):
            if self.send_rc_control:
                self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity, self.up_down_velocity,
                                           self.yaw_velocity)
            time.sleep(0.05)