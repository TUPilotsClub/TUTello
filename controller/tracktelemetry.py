from .telemetry import Telemetry
from drone import Tello

class TrackTelemetry(Telemetry):
    def __init__(self, tello: Tello):
        super().__init__(tello)

        self.target = (0,0)