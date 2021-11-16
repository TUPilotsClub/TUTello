from controller.telemetry import Telemetry
from drone.tello import Tello
from gui.simplegui import GUI, SimpleGUI
from video.videofeed import VideoFeed
from gui.videocomponent import VideoComponent
from controller.simplecontroller import SimpleController

print("started")
tello = Tello()
tello.connect()
telemetry = Telemetry(tello)
print("video")
video = VideoFeed(tello)
print("gui")
gui = SimpleGUI(video, telemetry)
print("controller")
controller = SimpleController(tello, gui)
gui.run()