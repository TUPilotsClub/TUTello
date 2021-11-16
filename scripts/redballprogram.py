from drone.tello import Tello
from gui.simplegui import SimpleGUI
from video.redballvideo import RedBallVideo
from video.facetrackvideo import FaceTrackVideo
from controller.trackcontroller import TrackController
from controller.tracktelemetry import TrackTelemetry
import sys

if sys.argv[1] != "webcam":
    tello = Tello()
    tello.connect()
else:
    tello = None
    #video = FaceTrackVideo(None)
telemetry = TrackTelemetry(tello)
video = RedBallVideo(tello, telemetry)
gui = SimpleGUI(video, telemetry)
controller = TrackController(tello, gui, telemetry)
gui.run()