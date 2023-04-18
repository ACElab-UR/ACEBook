# Programming the Roboflowers

This readme file explains the code of the roboflowers and details the whole step-by-step process of running experiments. For more details, please refer to the python modules for the full annotated code.

## Running experiments

### Starting an experiment
- connect the roboflower to the switch
- rename "expName" in the main.py of the HUB
- create a folder with the same name in the Home/Hub repository with the configurations YAML files inside:
  - contents.yaml
  - flowerGroups.yaml
  - rewardPatterns.yaml
  - UsedCodes.yaml
- modify these files accordingly depending on the experiment (see "Configuration YAML files" below)
- open main.py on the HUB via the terminal: python3 main.py
- start with a priming routine (probably 2 routines needed) (*p*) to check whether the pumps function properly and to allow the liquid to transit to the feeder
- start the experiment: *a*

### When an experiment starts:

When a roboflower boots, the raspberry pi runs by default the module "main.py" in home/roboflower, because of the line "python3 main.py" in flowerBoot.sh in the profile.d folder (rootfs/etc).

In main.py (Flower):
- import every main module in Flower: camera, electronics, MQTT from connect and routines
- instantiates a "cam" object from the Cam class in the camera module
- instantiates a "markers" object from the Markers class in the camera module
- instantiates a "feeder" object from the Feeder class in the electronics module:
	- the feeder object takes for arguments the 4 pins associated with motors from the Pump class in electronics, the pigpio daemon and the "UlForTurn" value 	for each pump
- instantiates a "led" object from the colorLED class in the electronics module:
	- the led object takes for arguments the RGB pins and the pigpio daemon
- instantiates a "mqtt" object from the MQTT class in the routines module
- makes a short routine to test that the red, green and blue pins work fine:
	- blink the 2 RGB LEDs in green for 2sec
	- blink the 2 RGB LEDs in blue for 2sec
	- blink the 2 RGB LEDs in red indefinitely until the flower receives a command from the HUB

- 3 cases depending on the command typed in the HUB:
1. if "mqtt.got_wakeup_message" = True (<=> typed "a" command in the console of the main.py of the HUB):
	- toggle "got_wakeup_message" to False
	- calls the "experiment" function from the routines module (see "Explanation of routines.py" what happens next)
2. if "mqtt.got_prime_message":
	- toggle"got_prime_message" to False
	- calls the "do_prime" method of feeder
3. if "mqtt.got_learn_message":
	- toggle "got_learn_message" to False
	- calls the colonylearn function of routines

### Training bees on the system

Before starting an experiment with the roboflowers, the colony needs to familiarise with the system. The learning mode should be "on" during the day and stopped every evening using the "q" command in the HUB to get the data of the day (log/debug files). See next section "Understanding the code/function "colonylearn" for all informations on how the learning mode works.

*note* in this mode: scent and quality are "None" and the retention time is set on 60second

- Step-by-step of the learning mode:
	- type "l" in the main.py of the HUB to start the function "colonylearn" from routines
	- the flowers all dispense 50uL of sucrose of a fixed quality of choice, and refill automatically every minute
	- at the end of the day, every bee marker is saved in a "seenmarkers" list displayed in the console of the HUB
	- log and debug files are created in the same way as in an experiment
	- every bee entering in a flower is recorded for 5seconds to check whether the bees learned successfully to use the system

### Configuration YAML files (HUB):
Each experiment depends on 4 configuration files which describe the characteristics of the flower meadow:

*note*: in these files, write the quality in milimol (example: 1000 for 1M), the quantity in ul*1000 (example 10000 for 10uL) and the retention in seconds.

- UsedCodes.yaml: stores the aruco markers used for the experiment
- flowerGroups.yaml: groups the flowers used in the experiment in 4 different flower groups: A, B, C and D
- contents.yaml: for each flower group, details the quality of the solution in pumps 1 and 2 and the colour of the flowers of this group
note: the fact that each flower has 2pumps give 2 opportunities of different rewards given by the same flower!
- rewardPatterns.yaml: 4 different bee groups: 1 to 4. In each of these bee groups you have the 4 flower groups A-D. For each group are precised the rewards that this group of bees will get when entering in the flowers of groups A-D:
	- the quality, quantity, scent and retention time <=> the "quality" then determines if pump 1 or 2 will give rewards to each bee!

RECAP of the configuration of an experiment:
- flowerGroups.yaml: determines which flowers belong to each flower group (4): A to D
	- example: fl1 and fl2 are in group A, fl3 and fl4 are in group B
- contents.yaml: determines the quality and scent of solution in pumps 1 and 2 + the colour of flowers for each group
	- example: group A: fl1 and fl2 are green:
			- pump 1 gives 1M sucrose
			- pump 2 gives 0.3M sucrose
		     group B: fl3 and fl4 are blue:
			- pump 1 gives 1.2M sucrose
			- pump 2 gives 1.6M sucrose
- rewardPatterns.yaml: - determines groups of bees (4): 1 to 4
			     - determines for each bee group and each flower group if the flowers give food from pump 1 or 2
	- example: - group 1: [bee markers 1 - 10]
				- flowers of group A (=green flowers) will give to this group:
					- quality 1 or 2 (determining if pump 1 or 2 will be at work for this bee!)
					- x quantity of solution
					- y scent (determining if pump 1 or 2 will be at work for this bee!)
					- the feeder will refill every z minutes (retention time)
				- flowers of group B (=blue flowers) will have:
					- quality a or b (determining if pump 1 or 2 will be at work for this bee!)
					- x' quantity of solution
					- y' scent (determining if pump 1 or 2 will be at work for this bee!)
					- the feeder will refill every z' minutes (retention time)
			- group 2: [markers 11 - 20]: idem!

This system allow each roboflower to be able to give 2 different types of (sucrose) solution. For each of these solution, the flower can give different quantities and have different retention times for each group of bees!

### Communication system - Mosquitto

Mosquitto is a messaging protocol (MQTT) taking care of the communication between the roboflowers and the main computer (HUB) in our system. See next section "Understanding the code/Mosquitto" for all informations about the communication system.

**Elements of the Mosquitto system:**
- **main computer** (<=> HUB) = publisher and broker. has the MQTT broker installed on it which acts as a central hub for all MQTT communication between the devices
- **switch** = network device: connects all the devices, including the main computer and Roboflowers, in a local area network (LAN)
- **roboflowers** = clients. They publish messages to topics or subscribe to topics to receive messages from other clients

### Getting data from experiments

See next section "Understanding the code/Explanation of connect.py" for all informations about the log and debug data files.

When running an experiment, data are logged in real-time to two data files:
- the debug files are the "human readable" version of the log files
- the log files are used to extract data from, in order to analyse them using python/excel

The debug files have a header of 3 variables: time, flower, message
	- the message element of debug files have one value: the event is explained in a clear sentence
The log files have a header of 8 variables: time, flower, id, pump, quality, scent, amount, event
	- the message element of log files are composed of 6 values: ID, pump, quality, scent, amount, event
		- these values are separated by commas and are meant to be extracted later to create a usable datasheet for experiment analysis


## Understanding the code

### Explanation of connect.py (HUB):
- contrary to the Flower module, the connect.py of the HUB also imports the "Thread" function from the threading library

A. the MQTT class
1. on_message function:
idem as in the connect.py of the Flower, except that the message to decode is not stored in last_message_received but is already in the format:
topic, timestamp, sender, mess

2. decode function:
receives two kind of topics; log/debug or commands:
- if the topic is log or debug:
	- calls the log method of the logger class and passes in the arguments: topic, timestamp, sender, and mess
- if the topic is commands:
	- if mess = turnedon: appends the ID of the sender (flower) to the ONflowers list
	- if mess = turnedoff: removes the flower ID to the ONflowers list
	- if mess = stillhere: appends the ID of the flower to the stillONflowers list and print "f4: still here" in the console of the main.py (because decode is called in the on_message function which is a callback of the MQTT class and is instantiated in the main.py)
	- if mess = awaits: 
		- assigns to a variable called "receiver" the "sender" elements of the message payload. example: f4
		- checks in which group f4 is in the flowerGroups dictionary: A, B, C or D
		- assigns to a variable called "yourgroup" the matching group letter
		- creates the variable "mess" later used in the connect.py of the flower! the structure of "mess" is taken from the YAML file "contents":
			- "quality_pump1, quality_pump2, scent_pump1, scent_pump2, colour_flower"
		- sends the "mess" to the sender (flower) through MQTT under the topic 'contents'
		- iterates through the lines of the rewardPatterns YAML file:
			- creates an empty "bees" variable
			- iterates through the "bees" in the current reward pattern
			- appends the ID of each bee separated by a hyphen to the "bees" string
			- generates a "mess" variable later used in the connect.py of the flower! the structure of "mess" is from the rewardPatterns YAML file:
				- "rewardPattern, bees, quality, quantity, scent, retention"
			- sends the "mess" to the sender (flower) through MQTT under the topic 'rewards'
	recap: the message "awaits" assigns the different elements of the system to the parameters in the configuration YAML files and waits for further instructions:

3. function "send":
this function points to receiver=all, meaning that every message (=load) published by the HUB is sent via MQTT to every flower!
- creates a "load" variable in the format: date/time - from HUB to sender: *message*
- publishes the load through the publish() method to the according topic
- print the load in the main.py of the HUB. example:  "date - from HUB to all: check"

4. function "keepchecking"
infinite loop that checks flowers present in the "ONflowers" list and sends a command message "check" to flowers every minute for them to respond with a
" - still here" if they are connected, and to respond with a " is not responding anymore" if not!
reminder: in the flower's "do" function, the command "check" sends a "stillhere" message under the "commands" topic. This "stillhere" message triggers the receiver (flower) to respond with a ": still here" if present in the "stillONflowers" list

5. function "do_keepchecking":
is a deamon (=thread) of the keepchecking function, so that it runs in a thread <=> in the background while the rest of the program can continue executing other functions.

6. function "stop":
simple function linked to the keepchecking and keepchecking deamon: stops the keepchecking loop and waits for the do_keepchecking thread to finish

B. The Logger class:
generates the log and debug files. The log() method within the class writes to these files:
*note* in the log file, quality is already in M and quantity in ul

- generates two files for log and debug in the data directory, and their name follow the following format:
	- 2023-03-19_13:23:00.log
	- 2023-03-19_13:23:00.debug
- opens the log and debug files in write mode and creates a header row with the following 8 variables:
	- log: 'time, flower, id, pump, quality, scent, amount, event'
	- debug: 'time, flower, message'

function "log":
writes to the log and debug files.
- takes as arguments: topic (either log or debug), t (timestamp), s (sender) and m (message)
- if topic = log:
	- extracts the 6 values from "m": "ID, pump, quality, scent, amount, event" and split them by commas
	*note* always check that any message sent to the log file have 5 commas <=> 6values!
	- opens the log file in append mode and writes a line of comma-separated values consisting of a total of 8 values (consistent with the header length):
            - timestamp, sender, m
	- print it to the console of main.py as well in the format:
		- time - f4, bee 10: pump1 gave xM of scent and yuL: event
- if topic = debug:
	- the message "m" in this case is just one element: the event. Debug does not report ID, pump, quality, etc.
	*note* always check that any message sent to the debug file no comma <=> 1value!
	- opens the debug file in append mode and writes a line of comma-separated values consisting of a total of 3 values:
            - timestamp, sender, m
	- print it to the console of main.py as well in the format:
		- time - f4: event

### Explanation of connect.py (Flower):
- the Client class from the library mqtt-paho is imported
- the client (= flower) subscribes to the topics "commands", "contents" and "rewards" <=> the flower will receive messages published to these topics by other clients connected to the broker
- lines 20-22 of the connect.py module:
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message 
These 3 callback functions are automatically executed when the MQTT class is instantiated somewhere: the class is called in the main.py of the flower, so the functions on_connect, on_disconnect and on_messages are executed in the main! and also any message will be printed in the console of this script :)
note: the function "decode" is also automatically executed in the main.py because is called in the on_message function. Same for the functions "do" which is called in the decode function, and "send".

1. function "on_message" from the MQTT class:
this function is responsible for transforming messages sent via MQTT (in bytes) into strings.
this new string message is parsed into 4 parts separated by dots: timestamp.sender.receiver.mess
these 4 elements are stored in a dictionary called last_message_received
The structure of the element "mess" from last_message_received depends on the topic of the MQTT message:
- if the topic = commands, the message is either: wakeup, kill, check, prime or learn
- if the topic = contents, the message looks like: quality_pump1, quality_pump2, scent_pump1, scent_pump2, colour_flower
- if the topic = rewards, the message looks like: reward_pattern, list-of-bees, quality, amount, scent, retention

2. function "decode":
the last_message_received is decoded by the decode function
- if the topic = commands: get the "message" element of last_message_received and apply it to the "do" function
- if the topic = contents: 
	- splits the "message" element of last_message_received and print it in the main.py of the flower as follow:
		"quality pump1: xM, quality pump2: yM"
		"scent pump1: *scent*, scent pump2: *scent*"
		"colour of flower: *colour*"
	- separates the different values of the message element in variables:
		- self.qualities = elements 1 and 2
		- self.scents = elements 3 and 4
		- self.color = element 5
	- sends 2 debug messages via the send() function:
		"pump 1 contains xM, *scent* solution"
		"pump 2 contains yM, *scent* solution"
	- "gotcontent" attribute becomes True
- if the topic = rewards:
structure of the self.rewardpatterns dictionary from the MQTT class:
{
    reward_pattern_1: {
        'bees': [bee_1, bee_2, ...],
        'amount': amount_value,
        'retention': retention_value,
        'quality': quality_value,
        'scent': scent_value,
        'pump': pump_number
    },
    reward_pattern_2: {
        'bees': [bee_1, bee_2, ...],
        'amount': amount_value,
        'retention': retention_value,
        'quality': quality_value,
        'scent': scent_value,
        'pump': pump_number
    },
    ...
}
	- takes the first element of "message" from last_message_received and make it a variable called rewardpattern
	- initializes an empty dictionary for the "rewardpattern" key in the self.rewardpatterns dictionary
	- assigns to the "bees" key the second element of "message" from last_message_received which is a list of bees and separate them with commas
	- creates variables associated with the next elements of "message" from last_message_received: quality, amount, scent and retention
	- based on whether the quality and scent of the incoming message corresponds to pump 1 or 2, sends a message to debug using the send function:
		- "reward pattern x is associated with pump 1" (or pump 2)
	- if the quality/scent don't match pumps 1 or 2, send a debug message:
		- "cannot find the correct pump"
	- sets the 'gotreward" attribute to True
	- prints in the console of the main.py of the flower: 
		- timestamp, flower, reward pattern 1 associated with pump 0
		- timestamp, flower, reward pattern 1 associated with pump 1
	
3. function "do":
- takes "command" as a parameter
- if the command = "wakeup":
	- sends "commands" and "turnedon" via the send() function (see below)
- if the command = "kill":
	- sends "commands" and "turnedoff" via the send() function
- if the command = check:
	- sends "commands" and "check" via the send() function
- if the command = prime:
	- sends "commands" and "received" via the send() function
- if the command = learn:
	- sends "commands" and "received" via the send() function
	
4. function "send": this function points to the HUB, meaning that every publication by the roboflowers are sent to the HUB
- takes 3 parameters: topic, message and receiver; receiver is set on "HUB"
- creates a string "load" in the format: current_time: flower_name HUB message
- publishes "load" to the specified topic using the publish() built-in function from paho library
- prints "load" in the console of the main.py of the flower. Example:
	Apr 5 14:50:21 2023 - from f4 to HUB: message (depends on the topic)

### Explanation of routines.py (Flower):

This module has 2 big functions: experiment and colonylearn. These 2 functions put together every module to make the whole system work, ie. the electronics part, the communication part, the camera and the configuration files.

*note:* the routines module, although using the classes and functions of every other module, interacts with them *only* in the main.py of the flower! When the experiment function is defined in routines, its arguments mqtt, led, cam, markers and feeders are instantiated in the main.py for it to use them.

A. function "experiment":
- takes 5 arguments: mqtt, led, cam, markers and feeder (defined as instances of MQTT, colorLED, Camera, Markers and Feeders of other modules in main.py)
- sends the message "I woke up" under the "debug" topic using the send method of the MQTT class
- blinks the RGB LEDs in green for 2sec using the blink method of colorLED class
- sends the message "awaits" under the topic "commands" using the send method <=> assigns the different elements of the system to the parameters in the configuration YAML files
- waits until mqtt.gotcontents and mqtt.gotrewards are updated to True to proceed
-     led.on(mqtt.colors[mqtt.color])  # turns on the RGB LEDs using the "on" method of the colorLED class and the color method of the MQTT class, fetching the right color from the config file
- prints the colour in the main.py of the flower
- starts the camera with the start() module of the Camera object and wait 2sec (for the camera to properly start)
- send messages under the topics debug and log:
	- to debug: "camera started" (because mess = 1 value in debug) and " save this time as: " (idem)
	- to log: " NA,NA,NA,NA,NA,started" (because mess = 6values in log)
	- creates an empty dictionary "thisbee" with 3keys: id, pump, amount
	- do a cleaning routine (<=> pump 3 = +12uL, pump 4= -21uL, pump 3 = +9uL) using the do_clean method of the function feeder

starts the experiment in a huge infinite loop: define the behaviour of the pumps and the communication for every bee scenario arriving/leaving the flowers:
- assigns to the variable "now" the current time
- captures frames from the camera using the grab() method of the cam object (instantiated in the main.py)
- detects markers in the frames using the detect() method of the markers object (idem)

- if markers.bee_arrived = True (method bee_arrived from the track method of the Markers class in Camera):
	- sends a message under the log topic in the format:
		- markers_last_seen,NA,NA,NA,NA,bee arrived'
	- toggle markers.bee_arrived to False

- if markers.bee_gone = True:
	- sends a message under the log topic in the format:
            - markers_last_seen,NA,NA,NA,NA,bee gone'
	- toggle markers.bee_gone to False

1. main big case: if the camera is currently detecting a marker (markers.being_seen) and the detected markers.ID is not None and the marker has not already been recognized (not markers.beenRecognized):
	- the recognize() method of the markers object takes in the rewardpatterns dictionary the reward pattern matching the bee ID
	- assigns it to "thisbeepattern" variable
	- if not markers.beenRecognized: say that an unexpected marker was seen and add this marker to "ID" + say it in debug
		- if the detected marker ID (str(markers.IDs[0][0])) is not in the second element of any tuple in the markers.beenNotified list (this second 			element contains the ID of a previously detected but not recognized marker):
			- send under the "debug" topic: " seen a  marker not expected: bee_ID"
		- in the list (markers.beenNotified), bees markers notified more than 30sec ago are removed from the list so that the camera can detect new markers
	a. if markers.beenRecognized <=> if a bee is being seen by the camera:
		- assigns to the "ID" variable markers.IDs[0][0] (= bee marker)
		- sends a message under the "debug" topic: " seen a marker: ID"
		- assigns to the "lastentered" variable this ID
		- if not feeder.full:
			- if ID in feeder.visitors: if the ID of the bee is already in the "visitors" dictionary of the feeder:
				- if the time elapsed since the last time the feeder was emptied for this bee ID is greater than the retention time:
					- sets for "thisbee" the ID, pump, amount, quality, and scent of the reward pattern for this bee
					- the feeder is filled using thisbee['pump'] and thisbee['amount'] values
					- sends under the "debug" topic: "giving to bee bee_id solution from pump X of quality YM and scent for Xul
					- sends under the "log" topic: "10,1,1.0,unscented,50.0,filling"
					- the "when_filled" key of the feeder.visitors[ID] dictionary is updated with the current time
				- if the retention time has not elapsed for thisbee:
					- sends under the "debug" topic: " I have seen bee_ID but the retention time has not elapsed'
					- sends under the "log" topic: bee_ID,NA,NA,NA,NA,retention'
			- if ID is not in feeder.visitors:
				- replace "thisbee[id] with the bee marker
				- replace thisbee[pump] and amount, quality and scents with according values in rewardspatterns
				- fill the feeder based on thisbee[pump] and amount
				- send under the "debug" topic: "giving bee_id solution from pump 1 of quality xM unscented for yul"
				- send under the "log" topic: "10,1,1.0,unscented,50.0,filling"
				- fill in the element "when_filled" of the key feeder.visitors[ID] with the current time
		- if feeder.full:
			- send under the "debug" topic: " the feeder is full already"
			- send under the "log" topic:  "bee_id,NA,NA,NA,NA,feeder full"
	b. if not markers.being_seen:
		- if feeder.full:
			- if it's been more than a minute that the feeder was last filled (for a previous bee):
				- send under the "debug" topic: " no bee, emptying the feeder"
				- send under the "log" topic: "NA,NA,NA,NA,NA,empty"
				- feeder.do_flush(80000) <=> pump 4 flushes out 80uL
				- sets the current time for the "when_emptied" element of the feeder.visitors[thisbee['id']] key
2. if mqtt.got_prime_message <=> receive a "p" command:
	- feeder.do_prime(): do the priming routine
	- toggle the got_prime_message to False
3. if mqtt.got_kill_message <=> receive a "k" command:
	- send under the "debug" topic: "I got turned off :( Goodnight!"
	- turns the RBG LEDs off
	- breaks from the experiment function

B. function "colonylearn":
- takes 5 arguments: mqtt, led, cam, markers and feeder just like the "experiment" function
- creates an empty list called "seenmarkers" (line not in experiment)
- sends the message "I woke up in learning mode" under the "debug" topic
- turns off the RGB LEDs
- sends the message "awaits" under the topic "commands" using the send method <=> assigns the different elements of the system to the parameters in the configuration YAML files
- starts the camera with the start() module of the Camera object and wait 2sec (for the camera to properly start)
- send under the "debug" topic: " camera started" followed by " save this time as 0"
- send under the "log" topic: "NA,NA,NA,NA,NA,LearnStarted'
- creates an empty dictionary "thisbee" with 3keys: id, pump, amount

starts the colonylearn in a big infinite loop: this function runs in the first days before an experiment to allow the bees of the colony to learn how to use the flowers:
*note* in this scenario: scent and quality are "None" and the retention time is set on 60seconds
- captures frames from the camera using the grab() method of the cam object (instantiated in the main.py)
- detects markers in the frames using the detect() method of the markers object (idem)
- *addition of colonylearn which is not in experiment*: displays the captured frame in a window called 'f' using the built-in imshow() function from opencv
- waits for 1 millisecond (necessary to ensure that the window is updated and remains responsive)

1. main big case: if the camera is currently detecting a marker (markers.being_seen) and markers.IDs is not None and has not already been recognized (not markers.beenRecognized):
	- toggle markers.beenRecognized to True
	- assigns to the "ID" variable markers.IDs[0][0] (= bee marker)
	- appends the bee marker to the "seenmarkers" list created at the beginning of the function [addition colonyLearn; not in experiment]
	- sends under the "debug" topic: "seen a marker: bee_id"
	- if not feeder.full <=> if empty feeder:
		- if more than 60sec have passed since the last time the feeder was emptied:
			- thisbee['id'] is set with the ID of the bee
			- sets the thisbee['pump'] to 0 <=> pump 1
			- sets thisbee['amount'] to 50000 <=> 50uL of sucrose, feeder completely full
			- sets "quality" and "scent" of thisbee to "null"
			- fills the feeder according to thisbee['pump'] and thisbee['amount'] values
			- sends under the "debug" topic: "giving bee_id solution from pump 1 of quality None and scent None for xul
			- sends under the "log" topic: bee_id,1,None,None,50,filling
		- if the feeder was last emptied less than a minute ago:
			- sends under the "debug" topic: " I have seen bee_id but the retention time has not elapsed"
			- sends under the "log" topic: "bee_id,NA,NA,NA,NA,retention"
	- if feeder.full:
		- sends under the "debug" topic: " the feeder is already full"
2. if no marker is being seen:
	- if feeder.full:
		- sends under the "debug" topic: " no bee: emptying the feeder"
		- feeder.do_flush(100000) <=> flushes out 100uL
3. if mqtt.got_prime_message:
	- feeder.do_prime()
	- toggle got_prime_message to False
4. if mqtt.got_kill_message <=> receive a "k" command:
	- send under the "debug" topic: "I got turned off :( Goodnight!"
	- [addition colonyLearn]: " in the end I have seen today: _bee_markers"
	- breaks from the experiment function


### Communication system - Mosquitto

Mosquitto is an open-source message broker that implements the MQTT (Message Queue Telemetry Transport) protocol. 
It is a lightweight publish/subscribe messaging protocol. MQTT is an ideal protocol for constrained devices such as sensors and microcontrollers.

### Functioning of the Mosquitto server

In Mosquitto, clients can connect to the broker and publish messages to topics or subscribe to topics to receive messages from other clients. The broker acts as a central hub for all messages, receiving and routing them to the appropriate clients based on their subscription interests.
Clients connect to the broker and communicate through packets, such as CONNECT, PUBLISH, SUBSCRIBE.

**Elements of the Mosquitto system:**
- **main computer** (<=> HUB) = publisher and broker. has an MQTT message broker installed on which acts as a central hub for all MQTT communication between the devices. 
- **switch** = network device: connects all the devices, including the main computer and Roboflowers, in a local area network (LAN).
- **roboflowers** = clients. They publish messages to topics or subscribe to topics to receive messages from other clients. 

The HUB is subscribed to these MQTT topics:
```python
	self.client.subscribe('commands')
	self.client.subscribe('log')
	self.client.subscribe('debug')
	self.client.subscribe('contents')
	self.client.subscribe('rewards')
```

The Roboflowers are subscribed to these MQTT topics:
```python
	self.client.subscribe('commands')
	self.client.subscribe('contents')
	self.client.subscribe('rewards')
```

### Programming the Mosquitto server

**1. Mosquitto on the HUB**

Setting up an MQTT communication between the main computer and the Roboflowers, i.e. installing the Mosquitto broker on the main computer:
- in the terminal: *sudo apt-get update*
- install the Mosquitto broker package: *sudo apt install mosquitto* - enable the Mosquitto broker to start automatically at boot time
- start the Mosquitto broker: *sudo systemctl start mosquitto* **or**:

- update Mosquitto to the latest version: *sudo apt-get upgrade mosquitto*

- restart the Mosquitto service to apply the changes: *sudo systemctl restart mosquitto*
- by default, Mosquitto broker listens on port 1883 for MQTT traffic. Verify that the Mosquitto broker is running: *sudo systemctl status mosquitto*
  
(If the broker is running, you should see a message that says "Active: active (running)" in the terminal window)

**2. Mosquitto on the Roboflowers**

Installing the Mosquitto client on the Raspberry pis:
- the paho-mqtt Python library takes care of integrating MQTT communication into the Python code running on the Raspberry Pis
- the mqtt.Client class creates an MQTT client that can connect to the Mosquitto broker

**3. Debugging MQTT**

Error: "MQTT already in use" : could mean that another MQTT broker or client is already running on the HUB and using the default MQTT port (1883). solution:
- stop the Mosquitto service: *sudo systemctl stop mosquitto*
- check if any other MQTT broker or client is running on the HUB: *sudo netstat -tlnp | grep 1883*
- kill the process, by replacing the PID with the right one (listed in the second column of output above): *sudo kill -s SIGTERM PID*
- start the Mosquitto service again: *sudo systemctl start mosquitto*