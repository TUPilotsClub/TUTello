from djitellopy.tello import Tello
from gui.simplegui import SimpleGUI
from gui.videofeed import VideoFeed
from controller.simplecontroller import SimpleController

print("started")
tello = Tello()
tello.connect()
print("video")
video = VideoFeed(tello)
print("gui")
gui = SimpleGUI(video)
print("controller")
controller = SimpleController(tello, gui)
gui.run()