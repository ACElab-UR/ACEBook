import pigpio  # for controlling GPIO pins on the Raspberry Pi
import time
from threading import Thread, Event
import yaml

pi = pigpio.pi()  # creates a connection to the local Raspberry Pi's GPIO pins using pigpio
with open(r'config.yaml') as file:  # opens the config.yaml file in read mode
    config = yaml.load(file, Loader=yaml.FullLoader)

pins = config['pins']  # retrieves the values associated with the 'pins' key in the YAML file
# and assigns it to the pins variable


# The colorLED class is responsible for controlling the RGB LEDs:
class colorLED:
    def __init__(self, redpin, greenpin, bluepin, pigpiodaemon):
        self.redPin = redpin
        self.greenPin = greenpin
        self.bluePin = bluepin

        self.pi = pigpiodaemon
        self.pi.set_mode(self.redPin, pigpio.OUTPUT)
        self.pi.set_mode(self.greenPin, pigpio.OUTPUT)
        self.pi.set_mode(self.bluePin, pigpio.OUTPUT)

    # turns off the LEDs by setting the duty cycle of all three pins to 0:
    def off(self):
        self.pi.set_PWM_dutycycle(self.redPin, 0)
        self.pi.set_PWM_dutycycle(self.greenPin, 0)
        self.pi.set_PWM_dutycycle(self.bluePin, 0)

    # blinks the LEDs by setting the frequency of all three pins to 10 Hz and the duty cycle of each pin
    # to the corresponding value in the color parameter divided by 4
    def blink(self, color, duration):
        self.pi.set_PWM_frequency(self.redPin, 10)
        self.pi.set_PWM_frequency(self.greenPin, 10)
        self.pi.set_PWM_frequency(self.bluePin, 10)

        self.pi.set_PWM_dutycycle(self.redPin, color[0] / 4)
        self.pi.set_PWM_dutycycle(self.greenPin, color[1] / 4)
        self.pi.set_PWM_dutycycle(self.bluePin, color[2] / 4)

        # wait for the specified duration
        time.sleep(duration)

    #  turns on the LEDs by setting the frequency of all three pins to 200 Hz and the duty cycle of each pin to
    #  the corresponding value in the color parameter
    def on(self, color):
        self.pi.set_PWM_frequency(self.redPin, 200)
        self.pi.set_PWM_frequency(self.greenPin, 200)
        self.pi.set_PWM_frequency(self.bluePin, 200)

        self.pi.set_PWM_dutycycle(self.redPin, color[0])
        self.pi.set_PWM_dutycycle(self.greenPin, color[1])
        self.pi.set_PWM_dutycycle(self.bluePin, color[2])


# The Pump class controls the 4 pumps with two motor pins: a forward pin and a backward pin and two encoder pins,
# one for each motor shaft:
class Pump:
    def __init__(self, fwdpin, bkwpin, leftencoder, rightencoder, pigpiodaemon, UlForTurn):
        self.counter = 0  # this attribute is used to count the number of encoder transitions
        # that occur during the pump's operation
        self.fwdpin = fwdpin  # this attribute stores the pin number for the motor's forward pin
        self.bkwpin = bkwpin

        self.leftEncoderPin = leftencoder
        self.rightEncoderPin = rightencoder
        self.leftEncoderLevel = 0  # this attribute stores the last known level of the left encoder pin (high or low)
        self.rightEncoderLevel = 0
        self.lastActivated = None  # this attribute stores the last motor pin that was activated (forward or backward)

        self.pi = pigpiodaemon
        self.pi.set_mode(self.fwdpin, pigpio.OUTPUT)
        self.pi.set_mode(self.bkwpin, pigpio.OUTPUT)

        self.pi.set_mode(self.leftEncoderPin, pigpio.INPUT)  # this line sets the mode of the fwd motor pin to output
        self.pi.set_mode(self.rightEncoderPin, pigpio.INPUT)

        self.pi.set_PWM_frequency(self.fwdpin, 200)  # this line sets the PWM frequency for the fwd motor pin to 200 Hz
        self.pi.set_PWM_frequency(self.bkwpin, 200)
        self.pi.set_PWM_dutycycle(self.bkwpin, 0)
        self.pi.set_PWM_dutycycle(self.fwdpin, 0)

        # sets up a callback function to be called whenever the level of the encoders pin change (= a transition occurs)
        self.pi.callback(self.leftEncoderPin, pigpio.EITHER_EDGE, self.transitionOccurred)
        self.pi.callback(self.rightEncoderPin, pigpio.EITHER_EDGE, self.transitionOccurred)

        self.delivering = False  # initializes an instance variable delivering to False. This variable is used to keep
        # track of whether the pump is currently delivering liquid or not

        # set two constants => stepsForTurn and UlForTurn:
        self.stepsForTurn = 700  # nb of steps required for the pump to make a full turn
        self.UlForTurn = UlForTurn  # volume of liquid (in µL) that is delivered in one full turn of pump (TO ADJUST)
        self.stepsForUl = int(self.stepsForTurn / self.UlForTurn)  # calculates the nb of steps required for the pump
        # to deliver one µL of liquid. It does so by dividing the stepsForTurn constant by the UlForTurn constant
        # and then rounding the result down to the nearest integer using the int() function.
        # This value is then stored in the stepsForUl instance variable.

        self._killer = False

    # the "deliver" function is responsible for delivering a specified volume of liquid at a specified speed:
    def deliver(self, volume, speed):
        if volume != 0:
            previouserror = None
            static = 0
            while static < 5:
                # this block of code calculates the error between the target volume and the actual volume that has been
                # delivered so far, and then checks if the error is within a certain range (here between -5 and 5).
                # If the error is within this range, it increments the value of static by 1 and prints its value:
                error = (volume / 1000) * self.stepsForUl - self.counter
                if error < 5 and error > -5:
                    static += 1
                    print("the current static is: " + str(static))
                # this block of code calculates an updated speed for the pump based on the current error value.
                # It then sets the duty cycle of the forward and backward pins of the pump based on the sign of the
                # updated speed:
                updatedspeed = error * 0.045
                if updatedspeed < 0:  # sets the duty cycle of the backward pin to the absolute value of the
                    # updated speed and the duty cycle of the forward pin to 0:
                    updatedspeed = min(updatedspeed, -100)
                    updatedspeed = max(-255, updatedspeed)
                    self.pi.set_PWM_dutycycle(self.bkwpin, -updatedspeed)
                    self.pi.set_PWM_dutycycle(self.fwdpin, 0)

                else:  # # the updated speed is > 0, sets the duty cycle of the forward pin to the updated speed and
                    # the duty cycle of the backward pin to 0:
                    updatedspeed = max(updatedspeed, 100)
                    updatedspeed = min(255, updatedspeed)
                    self.pi.set_PWM_dutycycle(self.fwdpin, updatedspeed)
                    self.pi.set_PWM_dutycycle(self.bkwpin, 0)

                # Add a delay of 1 millisecond between each step:
                #time.sleep(0.001)

                if self._killer:
                    break
        # If volume = 0, then infinite loop that will continue until the _killer flag has been set to True:
        else:
            while True:
                if self._killer:
                    print('here')
                    break
        # sets the duty cycle of both the forward and backward pins of the pump to 0, and then resets the value of
        # self.counter to 0 and sets the value of self.delivering to False:
        self.pi.set_PWM_dutycycle(self.bkwpin, 0)
        self.pi.set_PWM_dutycycle(self.fwdpin, 0)

        self.counter = 0
        self.delivering = False

    # The do_deliver function is called to start a delivery process for a specific volume and speed:
    def do_deliver(self, volume, speed):
        print("current volume and speed: " + str(volume) + ' ' + str(speed))  # so I know what happens
        self._killer = False
        self.delivering = True
        self.o = Thread(target=self.deliver, args=(volume, speed))
        self.o.daemon = True
        self.o.start()

    def stop(self):
        self._killer = True
        self.o.join()

    # This function transitionOccurred is a callback function that is called when a transition occurs in one of
    # the two rotary encoders that are connected to the pumps:
    def transitionOccurred(self, _gpio, _level, _tick):

        """
        Decode the rotary encoder pulse.

                     +---------+         +---------+      0
                     |         |         |         |
           A         |         |         |         |
                     |         |         |         |
           +---------+         +---------+         +----- 1

               +---------+         +---------+            0
               |         |         |         |
           B   |         |         |         |
               |         |         |         |
           ----+         +---------+         +---------+  1
        """

        # sets the current level of the encoder that had a transition in either the leftEncoderLevel or
        # rightEncoderLevel variable:
        if _gpio == self.leftEncoderPin:
            self.leftEncoderLevel = _level
        else:
            self.rightEncoderLevel = _level

        if _gpio != self.lastActivated:  # debounce mechanism to avoid false readings from the encoder
            self.lastActivated = _gpio

            # check the current state of both encoders and update the self.counter variable accordingly.
            # The self.counter variable keeps track of the total number of steps taken by the pump:
            if _gpio == self.leftEncoderPin and _level == 1:  # if the left encoder is triggered while the right
                # encoder is already triggered, it means the pump is moving in the forward direction and the counter
                # should be incremented
                if self.rightEncoderLevel == 1:
                    self.counter += 1
            elif _gpio == self.rightEncoderPin and _level == 1:  # if the right encoder is triggered
                # while the left encoder is already triggered, it means the pump is moving in the backward direction
                # and the counter should be decremented
                if self.leftEncoderLevel == 1:
                    self.counter -= 1


class Feeder:
    def __init__(self, deliverPump0, deliverPump1, waterPump, emptyPump):
        self.full = False  # variable used to indicate whether the feeder is full
        self.cleaned = False  # variable used to indicate whether the feeder has been cleaned
        self.filling = False  # variable used to indicate whether the feeder is currently being filled
        self.when_filled = None  # variable used to store the time when the feeder was filled
        self.when_emptied = -60  # variable used to store the time when the feeder was last emptied

        self.deliverPump0 = deliverPump0
        self.deliverPump1 = deliverPump1
        self.waterPump = waterPump
        self.emptyPump = emptyPump

        self.priming = False  # variable used to indicate whether the feeder is currently being primed

        self.visitors = {}  # variable used to keep track of the visitors to the feeder

    # the "do_flush" function is called to empty the feeder by running the empty pump for a specified volume of water:
    def do_flush(self, volume):
        self.emptyPump.deliver(volume=-volume, speed=255)  # runs the empty pump at full speed in reverse direction
        # to empty the feeder. The volume is passed in as a negative value to ensure that the pump runs
        # in the correct direction
        self.full = False  # indicates that the feeder is no longer full
        self.when_emptied = time.time()  # indicates when the feeder was emptied
        self.do_clean()  # calls the do_clean() method to clean the feeder after it has been emptied

    # the function "do_fill" is responsible for filling a specific pump with a given amount and speed:
    def do_fill(self, pump, amount=None, speed=255):
        if self.cleaned:  # if the cleaned flag is set to True (= the water pump delivered), the emptyPump (pump 4)
            # will pump back 12uL to flush out the water:
            self.emptyPump.deliver(-12000, 255)
        # determines which pump to fill. The corresponding pump is triggered to deliver fluid at the given
        # speed and amount. The "full" flag is also set to True to indicate that the pump is filled
        if pump == 0:
            self.deliverPump0.do_deliver(amount, speed)
            self.full = True
        elif pump == 1:
            self.deliverPump1.do_deliver(amount, speed)
            self.full = True
        elif pump == 2:
            self.waterPump.do_deliver(amount, speed)
            self.full = True
        elif pump == 3:
            self.emptyPump.do_deliver(amount, speed)
            self.full = True

    # the "clean" function is responsible for cleaning the feeder by running the water pump and empty pump in a
    # specific sequence:
    def clean(self):  # cleaning routine: what happens when the feeder is being cleaned:
        self.waterPump.deliver(12000, 255)  # water pump (pump 3) delivers 12uL of water to the feeder
        self.emptyPump.deliver(-21000, 255)  # empty pump (pump 4) flushes 21uL of liquid from the feeder
        self.waterPump.deliver(9000, 255)  # pump 3 delivers 9uL of water to the feeder (to avoid crystallisation of
        # potential remaining sucrose at the bottom of the feeder)
        self.cleaned = True

    def do_clean(self):
        self.o = Thread(target=self.clean)
        self.o.daemon = True
        self.o.start()

    # the "prime" function is used to prime the pumps before they are used:
    def prime(self):
        for i in range(5):  # repeats the priming routine (pumps 1-3 filling feeder + empty pump flushing out
            # behind them) 5times:

            # first, pump 1 delivers 20uL at full speed and pump 4 flushes out 25ul
            print('pump 1 delivers 20uL')
            self.deliverPump0.deliver(20000, 255)

            print('pump 4 flushes out 25uL')
            self.emptyPump.deliver(-25000, 255)

            # second, pump 2 delivers 20uL at full speed and pump 4 flushes out 25ul
            print('pump 2 delivers 20uL')
            self.deliverPump1.deliver(20000, 255)

            print('pump 4 flushes out 25uL')
            self.emptyPump.deliver(-25000, 255)

            # third, water pump (pump 3) delivers 20uL at full speed and pump 4 flushes out 25ul
            print('pump 3 delivers 20uL of water')
            self.waterPump.deliver(20000, 255)

            print('pump 4 flushes out 25uL')
            self.emptyPump.deliver(-25000, 255)

    def do_prime(self):
        self.o = Thread(target=self.prime)
        self.o.daemon = True
        self.o.start()



