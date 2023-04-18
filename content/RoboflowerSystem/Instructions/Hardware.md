# Hardware
In this section are detailed the specifics of the different electronic components of the Roboflowers.

## Motors
The Roboflowers use [mini brushed DC stepper motors](https://ecksteinimg.de/Datasheet/MO01052/Datenblatt.pdf) (see specifications of the motor)

**What is a stepper motor?**

Stepper motors are DC motors that move in discrete steps. They have multiple coils that are organized in groups called "phases". By energizing each phase in sequence, the motor will rotate, one step at a time. Typical stepper motors are 1.8 degrees per step, which is 200 steps per revolution.

**How to control the motors?**

On the PCB, the two [H-bridges](https://www.ti.com/lit/ds/symlink/l293d.pdf?ts=1678896509995&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FL293D) (= integrated circuits that enable a voltage to be applied in either direction) are responsible for controlling the motors of the pumps. 
These H-bridge include four independent half-H drivers that can control the direction and speed of DC motors. In our setup, the H-brigdes also serve as our stepper motors' driver boards. 

By sending signals through its GPIO pins, the Raspberry Pi can control the flow of current through the H-bridge circuits, hence controlling the movement of each peristaltic pump.
The Roboflowers have 2 full H-bridges:
- one is used to control the forward movement of the motors, providing a positive voltage
- the other is used to control the backward movement of the motors, providing a negative voltage

To move the motor in one direction, one pair of coils needs to receive a current while the other pair needs to be turned off.

## Pumps
In order to deliver precise amounts of liquid, our motors are programmed precisely to prevent issues such as missed steps or motor vibration. Some basics:
- delay: is the time interval between each step that the motor takes. This is an important parameter that determines the speed of the motor. The smaller the delay, the faster the motor will spin.
- static: is used to determine if the motor is stuck or not. In the code, static is a counter that keeps track of how many times the error is within a certain threshold (in this case, between -5 and 5): if the error is within the threshold for a certain number of times, it means the motor is not stuck and can continue to move.
- updatedspeed: this variable is the new speed that the motor will move at, based on the error calculated from the desired volume and the current position of the motor. It is calculated as error * 0.045 
- 0.045: is the constant that determines the relationship between the error and the updated speed. Increasing this value makes the motor turn faster because the updatedspeed variable is directly proportional to the error: increasing the constant can help to prevent the motor from getting stuck by ensuring that it is running at a fast enough speed to overcome any resistance or friction.
- 100 and -100: These are the minimum and maximum values for the updated speed

In the class Pump of the module electronics, each pump has its "UlForTurn" own method [*modification brought in the V2023.03.12*]
The "stepsForTurn" method corresponds to the number of steps required for the pump to make a full turn. This value is fixed and determined
by the design of the motor. In our design, 700steps make one full pump turn.


## PCB and components
The Printed Circuit Board is the "blue board" designed especially for the Roboflowers. It is used to connect and control the electronic components of the Roboflower, such as the LEDs and the motors.

Elements on the [PCB](file:///C:/Users/saaa/Documents/bumblebee_documents/RoboFlowerSystem/Circuit/Schematic_PeakEndFlowerShield%20H-bridge_2022-02-22.pdf) (Refer to the schematics for more info):
- U1 in the schematics represents the Raspberry pi <=> the 40 GPIO pins precisely
- JP1 - JP4: connectors for the pumps
- U2 and U3: H-bridges for controlling the motors of the pumps
- J2 + R13-14-15: connector for the two RGB LEDs: the one under the platform and the one in front of the roboflower
- U8: MT3608 Step Up <=> voltage booster or voltage regulator module that can increase the voltage level of the input voltage to a higher level

**J2 8p 2mm connector:**

"J" stands for "jack", convention used in electronics to name connectors. This connector is for the 2 RGB LEDs of the Roboflowers, which have 7 pins (2black wires connected to the same pin) spaced 2mm apart.

The J2 connector is connected to the two RGB LEDs using eight wires for 7 pins: two black wires for the anode and cathode (= connected to ground for all LEDs), two blue wires, two green wires, and two red wires. RGB LEDs are light emitting diodes that can produce a range of colors by varying the intensity of red, green, and blue light. The two RGB LEDs are wired in parallel and connected to the J2 connector.
The two RGB LEDs  receive the same voltage and current and emit the same colors at the same time, being wired in parallel. The Raspberry Pi sends the same PWM (Pulse Width Modulation) signals to each of the red, green, and blue elements of the LED to control the brightness and color of the LED.
Typically, the red wire is the positive (+) voltage supply, the black wire is the negative (-) voltage supply or ground, and the other wires are for the individual color channels of the RGB LED.

For example, one green wire might be connected to the green channel of the first RGB LED, and the other green wire might be connected to the green channel of the second RGB LED. The same applies to the other color channels, so there should be one red wire and one black wire for each RGB LED, and two wires for each of the three color channels (red, green, and blue).

**U1 (= Raspberry Pi):**

"U" is often used to represent an integrated circuit or, chip. These are small electronic components that contain many electronic circuits on a single chip of semiconductor material. They are often used in complex electronic systems to perform various functions. U1 means the first chip or integrated circuit in the circuit. U1 is the Raspberry Pi, responsible for controlling and communicating with all the other components on the PCB through its 40 GPIO pins.

**JP1 - JP4: connectors for the pumps:**

"JP" (for jumper) is a small piece of hardware that is used to connect two points or terminals on a circuit board. It is usually a small plastic block with pins. JP1 to JP4 are connectors for the motors of the roboflowers. They allow the motors to be easily connected and disconnected from the rest of the circuit.

Each JP connector has 6pins connected to 6 wires of the following colours: white, blue, green, yellow, black and red.
- white: is the "step" pin, which controls the movement of the stepper motor. The stepper motor moves in precise steps, and each step is triggered by a pulse on this pin
- blue: is the "direction" pin, which controls the direction of the stepper motor. Depending on the signal on this pin, the motor will move in either a clockwise or counterclockwise direction
- green: is the "enable" pin, which allows the motor to be turned on and off. When this pin is high, the motor is enabled and can move. When it's low, the motor is disabled and won't move
- yellow: is the "MS1" pin, which controls the microstepping mode of the motor driver. Microstepping allows for smoother and more precise movements of the motor, but it also requires more processing power and can be slower than full-step mode
- black: is the "ground" pin, which provides a reference voltage for the other pins.
- red: is the "power" pin, which provides the voltage for the motor

**U2 and U3: H-Bridges for the motors:**

the H-bridges are connected to the JP1 to JP4 connectors and to the GPIO pins on the Raspberry Pi. Some of the GPIO pins of the Raspberry pi are specifically connected to the H-bridges to control the direction and speed of the motors.

**U8, MT3608 Step Up:**

The MT3608 Step Up is a DC-DC converter that is commonly used to step up the voltage from a lower voltage source to a higher voltage level. The Raspberry Pi's GPIO pins provide a 5V voltage level, but our motors require a 6V voltage level. The MT3608 Step Up module has an inductor and a switching transistor. There is a back and forth exchange of current between the two change the magnetic which causes to change the voltage. Once the voltage has been boosted to 6V, it is sent to the motors through the H-bridge drivers, allowing the motors to operate at their optimal voltage level.


# Fixing hardware
In this section are detailed the most common problems you may face with the hardware.

## Pump problems

### One pump turns non-stop:
- Wiring issue: the signal to turn off the pump is not being received: double-check the wiring connections (green LED of the motor should be on)
- Calibration issue: the flow rate for the faulty pump is not properly set. Check the calibration values for this pump
- Motor issue: the pump is not responding to the signal to turn off. Try replacing the motor with a new one and see if the issue persists
- Mechanical issue: check the pump for any blockages or obstructions that may be preventing it from functioning properly

### One pump is turning in the wrong direction:
- Direction issue: check that the pump is turning anticlockwise when delivering solution from the bottle to the feeder
- Pump was mounted wrong: check that the pump was assembled correctly (see: AssemblingFlowers.md)
- Connector issue: check that the wires on the JP connectors are mounted correctly: white, blue, green, yellow, black and red

### The motor is vibrating but does not turn:
When a motor vibrates, it means it’s not receiving enough power to move past its initial position, so the motor is just moving very slowly. Check that the current received by the motor is enough (6V):
- set the multimeter to measure DC voltage: place cursor on 20V
- connect the probes to the power supply terminals of the motor:
	- the positive probe (red) touching the red wire on the JP connector
	- the negative probe (black) touching the black wire on the connector
	- make sure the motor is running while you take the measurement: this will give you an accurate reading of the voltage being supplied to the motor while it is under load
- lubricate the motor that gets stuck
- change constant in the code (0.045) and/or add time.sleep between each step motor step

## LEDs problems

### One of the LED doesn't light up during the routine when starting a Roboflower:
- Faulty LED: try swapping the LED with a known-working LED to see if the problem is with the LED itself
- Wiring issue: check the connections on the PCB and the J2 connector to ensure that the wires are connected properly and not loose
- Power issue: the power supply to the LED is not sufficient and is not getting enough voltage to light up. check the voltage levels using a multimeter to ensure that the power supply is providing the correct voltage:
    - Red LEDs typically require a voltage of around 1.8 to 2.2 volts to light up
    - Blue LEDs: around 3.0 to 3.6 volts to light up
    - Green LEDs: around 2.0 to 3.6 volts to light up

How to check the voltage levels of the LEDs with a multimeter:
- set the multimeter to measure DC voltage (usually denoted as V with a straight line and a dashed line above it)
- connect the black probe of the multimeter to the ground (GND) pin <=> touch the black pin of the connector on the PCB
- connect the red probe of the multimeter to the positive (+) pin of the power supply <=> touch the coloured pin of the connector on the PCB
