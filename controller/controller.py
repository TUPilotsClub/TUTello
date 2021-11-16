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

        self.update_func = None
        
        self._kill_thread = threading.Event()
        self._update_thread = threading.Thread(target=self.update, args=())
        self._update_thread.Daemon = True
        self._update_thread.start()

    def isKilled(self):
        return self._kill_thread.is_set()
            
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
        print("controller destruct")
        self._kill_thread.set()
        if self.tello != None:
            self.tello.end()
        
    def update(self):
        """ Update routine. Send velocities to Tello."""
        print("update thread", not self.isKilled())
        while not self.isKilled():
            if self._send_rc_control:
                self.tello.send_rc_control(self._roll_mag, self._pitch_mag, self._thrust_mag,
                                           self._yaw_mag)
            if self.update_func != None:
                self.update_func()
            time.sleep(self.COMMAND_FREQ)