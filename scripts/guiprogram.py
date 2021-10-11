from drone.tello import Tello
from gui.simplegui import GUI
from video.videofeed import VideoFeed
from gui.videocomponent import VideoComponent
from controller.simplecontroller import SimpleController

print("started")
tello = Tello()
tello.connect()
print("video")
video = VideoFeed(tello)
print("gui")
video_component = VideoComponent(video)
gui = GUI((video_component,))
print("controller")
controller = SimpleController(tello, gui)
gui.run()