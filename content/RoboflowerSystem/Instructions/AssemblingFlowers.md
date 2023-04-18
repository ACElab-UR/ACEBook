# Building the pumps

The Roboflowers are equipped with 4 peristaltic pumps, each bringing sucrose solution or water to the feeder inside the flowers via a tubing system:

- Pump 1 (or called 0 in python modules): delivers sucrose of concentration of choice
- Pump 2 (or called 1 in python modules): delivers sucrose of concentration of choice, or water
- Pump 3 (or called 2 or "waterpump" in python modules): delivers water to wash out sucrose from the feeder
- Pump 4 (or called 3 or "emptypump" in python modules): flushes out the mix of water/sucrose remaining in the feeder

## Mounting the pumps

### Crafting the pumps

Files for 3D printing the different pump parts in resin:

- Case and lid: [pumpV19_case_lid.sl1](..%2Fbumblebee_server%2F3D_Design%2FRoboFlower%2FPump%2FV19_final%2Fto_3d_print%2FpumpV19_case_lid.sl1)
- Impeller: [pumpV19_impellers.sl1](..%2Fbumblebee_server%2F3D_Design%2FRoboFlower%2FPump%2FV19_final%2Fto_3d_print%2FpumpV19_impellers.sl1)
- Pushers: [pushersV2_0.65_x25.sl1](..%2Fbumblebee_server%2F3D_Design%2FRoboFlower%2FPump%2FV19_final%2Fto_3d_print%2FpushersV2_0.65_x25.sl1) and [pushersV2_0.70_x25.sl1](..%2Fbumblebee_server%2F3D_Design%2FRoboFlower%2FPump%2FV19_final%2Fto_3d_print%2FpushersV2_0.70_x25.sl1)

Other elements:

- tubing (diameter 0.5mm): 0.5 * 0.5 * 100m silicone tubes
- [bearings](https://www.amazon.de/-/en/gp/product/B07MLZWJ4D/ref=ox_sc_act_title_2?smid=A2437MEP6E7G5L&psc=1): 2 * 5 * 2.5mm micro steel ball bearings
- [step motors](https://eckstein-shop.de/V-TEC6VMicro10x12mmDCMotorGleichstromGetriebeMotormitEncoder168RPM): see "Motors" section for all details
- various screws (sizes: 1.6; 2)

### Assembling the pumps

Step-by-step process:
- place the bearings x4 in the impeller
- place 1.6 screws in the case and screw motor to the bottom - must be tight
- cut tubing and place in the case
- gently place the impeller inside the case, facing down, until it "clicks"
- pull the tube out and try to fit two bearings around it - make sure the tubing goes around each bearing
- pull the tube to check that the bearings can roll freely
- place screws 2 (x4) on the lid on opposite ends
- screw the pushers (0.65 + 0.70) together with the tubing inside - pushers must be place on the right end of the tubing
- once the pump has been tested, rearrange the tubing so there is a long end on the right side of the pump, and short end on the left side

The peristaltic pumps have a left and right end. When moving forward, the motors turn anticlockwise, making the pump turning anticlockwise as well: liquid flows from the right to the left. For this reason, the pushers are mounted on the right end of the tubing: while the pumps is running, the pushers get pushed against the case of the pump and does not displace the tubing to the left due to rotary force.

### Testing the pumps

The pumps (x4 per flower) need to be tested individually to know exactly how much they push liquid per motor turn. The testing is done using a Roboflower containing the following elements:
- Raspberry pi
- SD card called "TEST" containing the flower files + the pumpTest module
- Picam connected to the camera connector (needed to avoid a python error)
- PCB mounted on the Raspberry pi
- Pump that needs to be tested on the motor #1 connector

Connect the pump to a syringe containing water and let the other end of the tube lose on the table next to a ruler

#### Pump delivering calculation
Plug the raspberry pi (power cord, HDMI cable and keyboard). Once the raspberry pi is done booting, type:
```python
python3 -i pumpTest.py
feeder.deliverPump0.deliver(18000, 255)  # 18000 corresponds to 3 full pump turns (pumps are calibrated on one motor turn = 6uL delivered)
```
This module allows the pump to connect to the PCB's motor connector "0" and deliver 18uL of liquid
Repeat 3times per pump and calculate the mean of water progression (in mm). Make sure that the motor turns effortlessly and that the water flow is consistent. The water progression should be similar in the 3 occurrences - if too variable, discard the pump.

/!\ before calibrating any pump: connect them to a bottle full of water turned upside down and make sure that water doesn't flow through the tubing!
The tubing being really small, there is a risk of water travelling in the tubing through capillarity. If it is the case: discard the pump

### Pump calibration
Method for calibrating a pump:
- run the peristaltic pump for a set number of motor turns, such as 3 turns (=18000)
- /!\ make sure that the motor is running clockwise
- measure the distance between the mark you made on the silicone tubing and the point where the water level has moved to on a graduated ruler
- divide the distance moved by the water by the number of motor turns to get the amount of water delivered per turn of the motor
- repeat this step 3times for more precision
- /!\ if water continues moving through the tube at rest: discard the pump!
- convert this average distance to microliters pushed by one motor turn with the following formula:
	- cross-sectional area of the tubing = πr^2, with r is the radius of the tubing (so 0.25mm in our system because the diameter of the tubing is 0.5mm
	- volume delivered per motor turn (in ul) = cross-sectional area of tubing (in mm^2) x distance moved by water (in mm)
	
For example, if the water moved 10 mm in the calibration test, then the volume delivered per turn would be:
	- volume delivered per turn ≈ 0.196 mm^2 x 10 mm = 1.96 μL per turn (approximately)

Use this [website](https://www.omnicalculator.com/math/cylinder-volume) for easy calculation, with these parameters:
  - radius (in mm) = 0.25
  - diameter (in mm) = 0.5
  - height (in mm) is the distance the water has moved along the graduated ruler
  - volume (in mm^3) is the volume delivered per motor turn for this pump (because 1mm^3 == 1uL)

Pumps range: around 30mmn for one pump full turn <=> approx. 5.5 - 6.5uL per motor turn

## Programming the pumps

Once 4 pumps deliver correctly they can be labelled and registered accordingly in the "calibration_pumps" Excel sheet:
- date of testing
- method for testing the pump (to check for consistency): calibration station or experiment
- associate pumps with 1, 2, 3 and 4: try associating pumps 1 and 2 with the most precise pumps

When done, modify the code accordingly with the delivering power of each pump:

In the main module of the flower:
```python
feeder = electronics.Feeder(electronics.Pump(electronics.pins['motor1fwd'], electronics.pins['motor1bkw'],
		 electronics.pins['motorClk1'], electronics.pins['motorDt1'],
		 electronics.pi, UlForTurn= # value pump1),
		 electronics.Pump(electronics.pins['motor2fwd'], electronics.pins['motor2bkw'],
		 electronics.pins['motorClk2'], electronics.pins['motorDt2'],
		 electronics.pi, UlForTurn= # value pump2),
		 electronics.Pump(electronics.pins['motor3fwd'], electronics.pins['motor3bkw'],
		 electronics.pins['motorClk3'], electronics.pins['motorDt3'],
		 electronics.pi, UlForTurn= # value pump3),
		 electronics.Pump(electronics.pins['motor4fwd'], electronics.pins['motor4bkw'],
		 electronics.pins['motorClk4'], electronics.pins['motorDt4'],
		 electronics.pi, UlForTurn= # value pump4))
```

*note*: see Hardware.md section "fixing pumps problems" if something doesn't work with the pump


# Assembling the Roboflowers

Step-by-step process to build a Roboflower from scratch, or to rebuild a flower after cleaning the different elements in-between experiments

3D design of the complete Roboflower: [RoboFlower.FCStd1](..%2Fbumblebee_server%2F3D_Design%2FRoboFlower%2FRoboFlower.FCStd1)

## Roboflower elements
- Raspberry pi model 4 - 4Go
- SD card flashed with classic ubuntu distribution + Roboflower files
- PCB
- 3D printed parts: flower halves x2: left and right; flower bases x2: top and bottom
- Feeder (max capacity = 50uL)
- PiCamera
- Polycarbonate glass pieces x2 (offers high optical clarity): landing platform and camera piece  
- Grey spray cans for colouring the flower halves and match the arena wall and floor
- white LED x1: to light the inside of the flower so the camera can detect markers 
- RGB LEDs x2 wired in parallel: colours of the flower: one on the front of the flower, the over below the landing platform
- Peristaltic pumps x4
- Connectors for the LEDs and pumps
- Various screws


## Raspberry pi
The Raspberry Pi 4 is the SBC (single-board computer) used for the Roboflowers. We use the RPI 4 which has, among other things:
- 4GB of RAM
- Ethernet connectors
- Bluetooth 5.0
- one micro-SD card slot
- two micro-HDMI ports
- camera connector (CSI-2)

First, check if the Raspberry pi is working, especially:
- if it can read the SD card (see next section)
- if the camera connectors work properly (i.e. no camera error after the rpi is done booting)

To test these, plug the raspberry pi (power cord + HDMI cable) with a flashed SD card and connect a camera to the CSI connector

## SD card and Roboflower files
To use the Raspberry Pi, an OS (operating system) has to be installed on the SD card. The most popular OS for the RPI is the Raspberry Pi OS (formerly known as Raspbian), which is based on Debian Linux.

The installation we use for the roboflowers is based on the Raspberry Pi Lite OS 32-bit (2023.02.21). This "Flower0"
needs to be flashed on an empty SD card for every new flower. /!\ note that Flower0 doesn't have a desktop environment (because it uses a lot of system resources. This means that they cannot display videos because there is no graphical user interface (GUI).

Step-by-step process for flashing a new SD card with Flower0:
- insert the SD card on your computer (Windows works too) - has to be 4Go minimum
- open the Raspberry Pi Imager software and choose the OS you want to install (Flower0)
- select the SD card as the target for the installation
- click "Write" and wait for the process to finish

Once the operating system is installed on the SD card, you can insert the SD card into the Raspberry Pi and power it on

Additional infos about the Roboflowers' OS:
  - login: roboflower
  - psw: ACElab

- "Flower0_original" is the OS created by Massimo in 2021
- Flower0 is the new OS used in the current roboflowers
- additional packages installed: pip3, opencv, paho mqtt, picamera, pigpio, yaml, wiringpi

Once done, some files need to be modified. (/!\ has to be done on an Ubuntu machine to be able to access the partitions on the SD card:
- in the "home/roboflower" folder, place the Flower files and:
  - modify the *config.yaml* with the matching flower number (by convention, use the number noted on the Raspberry pi board)
  - modify the *main.py* with the according delivering values of each pump

- in the "etc" folder, modify the *dhcpcd.conf*:
  - open terminal in the target folder: *sudo nano dhcpcd.conf*
  - de-comment lines of the "eth0" block of code (minus the line \6) and rename the IP address of the flower. Format: 192.168.0.112 (flower 12)

/!\ forcing a fixed IP creates problem accessing internet via wifi or ethernet. Re-comment lines
in dhcpcd.conf if you ever want to reconnect your raspberry pi to internet.

## Camera
For the Roboflowers, we use the PiCamera which is a camera module designed specifically for the Raspberry Pi. It connects to the CSI (Camera Serial Interface) port on the Raspberry Pi board and is controlled using the Python Picamera library.

We use the Picamera to recognize the aruco markers on the bees using the library OpenCV in Python.

### Detecting the bees:

Individual bees are marked with ArUco codes on their thorax. ArUco is a popular library in Python for marker-based augmented reality applications. ArUco markers consist of squares with each
cell of the pattern being either black or white. The pattern is surrounded by a white border to make detection easier. 
The python library associated provides a pre-defined set of marker dictionaries, each containing a set of unique
markers with different sizes and resolutions.

The roboflowers are using the DICT_4X4_250 dictionary, which consists of 250 unique 4x4 bit patterns, each representing 
a unique ID. For the Roboflowers, we are using only the 99 first markers (largely enough for one experiment). 


### Calibrating/testing the camera:

Once the raspberry pi connectors recognize the PiCamera, the focus of the camera needs to be adjusted manually to ensure that the ArUco codes on the bees are captured clearly and not blurred.

  - start the Raspberry pi with the camera in one flower half, with the glass piece in front and the marked dummy bumblebee in position in front of the feeder

## LEDs
Each Roboflower has 2 RGB LEDs wired in parallel, and one white LED. Make sure that the RGB LEDs light up in each colour (Red, Green and Blue)
when the flower is booting, before starting an experiment. The white LED should be turned on at all times.



