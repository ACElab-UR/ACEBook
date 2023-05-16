# Roboflower System

Welcome to the repository of the Roboflower system!

The Roboflowers are automated artificial flowers from the [ACElab](https://www.animal-economics.com/tjczaczkes) used in behavioural experiments on bumblebees. This READme file details everything about the system, from building the roboflowers to programming experiments, as well as debugging the system. 

Please refer to this document before using the Roboflowers.

## Files in the repository:

### Instructions
Find the readme files to assemble, program and debug the Roboflowers:

- Programming.md
- Assemblingflowers.md
- Harware.md

### Versions
Find the annotated python modules for each Roboflowers' version

### Circuit
Find the schematics and gerber files for the Roboflowers' PCB

### Misc
Find the aruco codes and various files for updating the Roboflower system

## Log changes:
Track the changes brought to the Roboflowers in each version:

### V2023.03.12:
- all python modules are now annotated for clarity
- pumps now have individual calibration rather than one calibration for all 4 pumps per flower
- new operating system for the roboflowers:
	- latest upgrades and updates for packages
- main.py of the HUB re-written in a simpler way
- connect.py (HUB) modifications:
	- the connection with the flowers is now checked every minute 
- main.py (Flower) modifications:
	- pumps' UlForTurn are now invididually precised for each roboflower
	- routine for testing that the RGB LEDs are working properly
- connect.py of the Flower modifications:
	- addition of a "on_disconnect" function that tries to reconnect the flower if it loses the connection with the broker
- electronics.py of the Flower modifications:
	- addition of the parameter "UlForTurn" in the Pump class
	- addition of the parameter "duration" in the blink method
	- precision of the exact volumes delivered in the priming routine in the "prime" function

### V2023.04.13:
In this version: the roboflowers are stable and work well!
- corrected the "too many values to unpack" bugs in routines.py
- fixed the on_disconnect function in both connect.py
- all modules further annotated for clarity
- improved the way log and debug files are written
- corrected the camera error in colonylearn

### V2023.05.04:
- in Electronics:
 	- increased the amount flushed out by the empty pump from 20 to 25ul (to avoid any leaking risk due to calibration inprecision
 	- in the clean() function, empty pump now flushes out 25ul instead of 21ul 
 	- changed back the "error" from -100/100 to -95/95 for the pumps
- hardware:
 	- changed the big milkers for glass bottles which are no longer suspended above the flowers (reduce capillary action in the tubes + risk of flooding the flowers)
 	- removed the glass pieces in the flowers because of condensation and droplets
