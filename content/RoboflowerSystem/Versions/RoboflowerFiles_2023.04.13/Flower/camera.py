import cv2  # library for computer vision
from cv2 import aruco  # for detecting and identifying markers
from picamera.array import PiRGBArray  # for processing camera input
from picamera import PiCamera  # for interacting with the Raspberry Pi camera
from threading import Thread
import time


# class "Cam" for interacting with the Raspberry Pi camera:
class Cam:
    def __init__(self):
        self.camera = PiCamera()  # initializes an instance of the PiCamera class
        self.camera.resolution = (320, 240)  # sets the camera resolution to 320x240 pixels
        self.camera.framerate = 30  # 30 frames per second
        self.raw = PiRGBArray(self.camera, size=self.camera.resolution)
        # sets up a continuous capture stream from the camera, with raw image data format in Blue-Green-Red color
        # scheme, and using the video port for better performance:
        self.stream = self.camera.capture_continuous(self.raw,
                                                     format="bgr",
                                                     use_video_port=True)

        self.frame = None  # initializes a variable to store the current camera frame
        self.stopped = False  # initializes a variable to keep track of whether the camera is stopped or not

    #  function "read" reads frames from the camera stream and store them in the self.frame variable:
    def read(self):
        for f in self.stream:  # loops through the camera stream and captures each frame
            self.frame = f.array  # stores the current frame in the self.frame variable
            self.raw.truncate(0)  # clears the camera buffer (= temporary storage where images captured by the
            # camera are stored before they are processed)
            if self.stopped:  # if the camera is stopped:
                self.stream.close()  # closes the camera stream
                self.raw.close()  # clears the camera buffer
                self.IO.close()  # returns from the function
                return

    def start(self):
        self.t = Thread(target=self.read)
        self.t.daemon = True
        self.t.start()

    #  returns the most recently captured frame from the camera buffer. This method is called when we want to access
    #  the latest frame captured by the camera:
    def grab(self):
        return self.frame

    def stop(self):
        self.stopped = True


# the class "Markers" is responsible for detecting and tracking ArUco markers using the OpenCV library.
# The detected markers will be used to identify the bees as they enter and exit the automated flower:
class Markers:
    def __init__(self):
        self.existing = aruco.Dictionary_get(aruco.DICT_4X4_250)  # this line initializes the ArUco dictionary.
        # The aruco.Dictionary_get() method is used to retrieve the dictionary with the specified size and ID,
        # which in this case is the 4x4 dictionary with ID 250
        self.IDs = []  # initializes an empty list to store the IDs of the detected markers

        self.params = aruco.DetectorParameters_create()  # initializes a set of detection parameters for the ArUco
        # marker detector. This object is used to set various parameters for the detector algorithm,
        # such as adaptive threshold sizes and marker size thresholds:
        # self.params.adaptiveThreshWinSizeMin=48
        # self.params.adaptiveThreshWinSizeMax=60
        # self.params.adaptiveThreshWinSizeStep=4

        print(self.params)  # prints the detector parameters to the console for debugging purposes
        self.being_seen = False  # initializes a boolean variable to keep track of whether or not the marker
        # is currently being seen by the camera
        self.beenRecognized = False  # idem as above, but if currently being recognized
        self.bee_arrived = False  # whether a bee has arrived at the flower
        self.bee_gone = False  # whether a bee has left the flower
        self.last_seen = None  # initializes a variable to store the last time the marker was seen by the camera
        self.beenNotified = []  # stores the IDs of the markers that have already been recognized
        self.absence = 0  # initializes a counter variable to keep track of the number of frames the marker
        # has been absent from the camera
        self.presence = 0  # same as above, but number of frames the marker has been present in the camera

    # the "detect" function is responsible for detecting the Aruco markers in a given frame. It takes a frame as input
    # and updates the IDs and corners attributes of the Markers class with the detected markers:
    def detect(self, frame):
        # use the aruco.detectMarkers() function to detect the Aruco markers in the given frame. The self.existing
        # attribute is a dictionary of the Aruco markers that the system is looking for:
        corners, self.IDs, rejected = aruco.detectMarkers(frame, self.existing, parameters=self.params)
        self.track()  # responsible for keeping track of the presence or absence of bees around the flower

    # the "track" function is responsible for tracking the presence of markers in the camera frame over time:
    def track(self):
        if self.IDs is not None:
            self.presence += 1
            self.absence = 0
            if self.presence >= 30/3:  # this condition checks if the marker has been present for at least 10 frames
                if self.being_seen is False:  # this condition checks if the marker was not previously being seen.
                    # If it wasn't, it means that a new bee has arrived at the flower, so we set being_seen to True:
                    self.being_seen = True
                    self.bee_arrived = True
                    self.last_seen = self.IDs[0][0]
        elif self.being_seen:
            self.absence += 1
            self.presence = 0
            if self.absence >= 30*10:
                self.being_seen = False
                self.beenRecognized = False
                self.bee_gone = True  # to indicate that a bee has left the flower
                self.presence = 0
                self.absence = 0

    # this "recognize" function is responsible for recognizing the specific reward pattern that the detected bee
    # belongs to, based on its aruco marker ID:
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
