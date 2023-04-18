import time
import cv2
import camera

# initialises instances from the camera module, such as the markers and the cam functions, and starts the camera:
cam = camera.Cam()
markers = camera.Markers()
cam.start()
time.sleep(2)
now = time.time()

while True:
    frame = cam.grab()  # captures a frame from the camera using the "grab()" method of the cam object
    markers.detect(frame)  # detects markers in the captured frame using the "detect()" method of the markers object
    cv2.imshow('f', frame)  # displays the captured frame with detected markers in a window
    cv2.waitKey(1)  # required for the window to be displayed correctly
    print("the current marker is: ", markers.IDs)  # this line prints the IDs of the detected markers to the console
    print("the camera is currently recording at ", 1/(time.time()-now), " frames per second")  # this gives the number
    # of frames per second the camera is capturing
    now = time.time()  # this line updates the now variable to the current time for the next FPS calculation
