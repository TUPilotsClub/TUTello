from drone.tello import Tello
from gui.simplegui import GUI
from video.videofeed import VideoFeed
from controller.simplecontroller import SimpleController

print("started")
tello = Tello()
tello.connect()
print("video")
video = VideoFeed(tello)
print("gui")
gui = GUI(video)
print("controller")
controller = SimpleController(tello, gui)
gui.run()