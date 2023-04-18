import cv2
from cv2 import aruco
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread

import time

class Cam:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (320, 240)
        self.camera.framerate = 30
        self.raw = PiRGBArray(self.camera, size=self.camera.resolution)
        self.stream = self.camera.capture_continuous(self.raw,
                                                     format="bgr",
                                                     use_video_port=True)
        
        self.frame = None
        self.stopped = False

    def read(self):
        for f in self.stream:
            self.frame = f.array
            self.raw.truncate(0)
            if self.stopped:
                self.stream.close()
                self.raw.close()
                self.IO.close()
                return

    def start(self):
        self.t = Thread(target=self.read)
        self.t.daemon = True
        self.t.start()

    def grab(self):
        return self.frame

    def stop(self):
        self.stopped = True


class Markers:
    def __init__(self):
        self.existing = aruco.Dictionary_get(aruco.DICT_4X4_250)
        self.IDs = []

        self.params = aruco.DetectorParameters_create()
        #self.params.adaptiveThreshWinSizeMin=48
        #self.params.adaptiveThreshWinSizeMax=60
        #self.params.adaptiveThreshWinSizeStep=4

        print(self.params)
        self.being_seen = False
        self.beenRecognized = False
        self.bee_arrived = False
        self.bee_gone = False
        self.last_seen = None
        self.beenNotified = []
        self.absence = 0
        self.presence = 0

    def detect(self, frame):
        corners, self.IDs, rejected = aruco.detectMarkers(frame, self.existing, parameters=self.params)
        self.track()

    def track(self):
        if self.IDs is not None:
            self.presence +=1
            self.absence = 0
            if self.presence >= 30/3:
                if self.being_seen == False:
                    self.being_seen = True
                    self.bee_arrived = True
                    self.last_seen = self.IDs[0][0]
        elif self.being_seen:
            self.absence += 1
            self.presence = 0
            if self.absence >= 30*10:
                self.being_seen = False
                self.beenRecognized = False
                self.bee_gone = True
                self.presence = 0
                self.absence = 0
                
    def recognize(self, rewardpatterns):
        ID = self.IDs[0][0]
        if ID in rewardpatterns[1]['bees']:
            thisbeepattern = 1
            self.beenRecognized = True
        elif ID in rewardpatterns[2]['bees']:
            thisbeepattern = 2
            self.beenRecognized = True
        elif ID in rewardpatterns[3]['bees']:
            thisbeepattern = 3
            self.beenRecognized = True
        elif ID in rewardpatterns[4]['bees']:
            thisbeepattern = 4
            self.beenRecognized = True
        else:
            thisbeepattern = None
            self.beenRecognized = False
        return thisbeepattern
