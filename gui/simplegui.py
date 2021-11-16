from controller.telemetry import Telemetry
from .gui import GUI
from .guicomponent import GUIComponent
from .videocomponent import VideoComponent
from .textcomponent import TextComponent
from video.videofeed import VideoFeed
from gui import GUI

class SimpleGUI(GUI):
    def __init__(self, videofeed: VideoFeed, telemetry: Telemetry):
        if not isinstance(videofeed, VideoFeed):
            raise TypeError("Parameter 'videofeed' should be of type VideoFeed")
        
        videocomponent = VideoComponent(videofeed)
        textcomponent = TextComponent("variable string: {test}", (800, 800), is_constant=False)
        textcomponent.setKeyValue("test", "tested")
        components = (videocomponent, textcomponent)
        super().__init__(components)