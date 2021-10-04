from drone import Tello

class Telemetry:
    def __init__(self, tello: Tello):
        self.tello = tello

    def getBattery(self):
        return self.tello.battery

    def getBarometer(self):
        return self.tello.barometer

    def getFlightTime(self):
        return self.tello.flight_time

    def getRoll(self):
        return self.tello.pitch

    def getRoll(self):
        return self.tello.roll

    def getYaw(self):
        return self.tello.yaw

    def getSpeedX(self):
        return self.tello.speed_x

    def getSpeedY(self):
        return self.tello.speed_y

    def getSpeedZ(self):
        return self.tello.speed_z

    def getTempLow(self):
        return self.tello.temperature_lowest

    def getTempHigh(self):
        return self.tello.temperature_highest

    def getFlightDistance(self):
        return self.tello.distance_tof

    def getHeight(self):
        return self.tello.height

    def getAccelerationX(self):
        return self.tello.acceleration_x

    def getAccelerationY(self):
        return self.tello.acceleration_y

    def getAccelerationZ(self):
        return self.tello.acceleration_z
                    