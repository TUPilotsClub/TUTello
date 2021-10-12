from gui.simplegui import SimpleGUI
from video.filteredvideo import FilteredVideo
import cv2

def gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def blur(gray):
    return cv2.GaussianBlur(gray, (5,5), 0)

def edges(gray):
    return cv2.Canny(gray, 30, 150)

# create video object which converts to gray, then blurs, then does edge detection
video = FilteredVideo(None).then(gray).then(blur).then(edges)

gui = SimpleGUI(video)
gui.run()