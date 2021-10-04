from drone.tello import Tello
from gui.simplegui import SimpleGUI
from video.redballvideo import RedBallVideo
from controller.simplecontroller import SimpleController
import sys

if sys.argv[1] != "webcam":
    tello = Tello()
    tello.connect()
    video = RedBallVideo(tello)
else:
    video = RedBallVideo(None)
gui = SimpleGUI(video)
gui.run()