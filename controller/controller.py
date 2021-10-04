from drone.tello import Tello
import threading
import time

class Controller:
    COMMAND_FREQ = 0.05

    def __init__(self, tello: Tello):
        self.tello = tello
        
        self._pitch_mag = 0
        self._roll_mag = 0
        self._thrust_mag = 0
        self._yaw_mag = 0
        self._send_rc_control = False
        
        self._update_thread = threading.Thread(target=self.update, args=())
        self._update_thread.Daemon = True
        self._update_thread.start()
        
            
    def addPitch(self, speed):
        self._pitch_mag += speed
            
    def minusPitch(self, speed):
        self._pitch_mag -= speed
        
    def addRoll(self, speed):
        self._roll_mag += speed
        
    def minusRoll(self, speed):
        self._roll_mag -= speed
        
    def addYaw(self, speed):
        self._yaw_mag += speed
        
    def minusYaw(self, speed):
        self._yaw_mag -= speed
        
    def addThrust(self, speed):
        self._thrust_mag += speed
        
    def minusThrust(self, speed):
        self._thrust_mag -= speed

    def setPitch(self, speed):
        self._pitch_mag = speed

    def setRoll(self, speed):
        self._roll_mag = speed

    def setYaw(self, speed):
        self._yaw_mag = speed

    def setThrust(self, speed):
        self._thrust_mag = speed
        
    def takeoff(self):
        print("takeoff")
        self.tello.takeoff()
        self._send_rc_control = True
        
    def land(self):
        print("land")
        self.tello.land()
        self._send_rc_control = False
        
    def destruct(self):
        self.tello.end()
        
    def update(self):
        """ Update routine. Send velocities to Tello."""
        while (True):
            if self._send_rc_control:
                self.tello.send_rc_control(self._roll_mag, self._pitch_mag, self._thrust_mag,
                                           self._yaw_mag)
            time.sleep(self.COMMAND_FREQ)