import pigpio
import time
from threading import Thread, Event
import yaml

pi = pigpio.pi()
with open(r'config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

pins = config['pins']


class colorLED:
    def __init__(self, redpin, greenpin, bluepin, pigpiodaemon):
        self.redPin = redpin
        self.greenPin = greenpin
        self.bluePin = bluepin

        self.pi = pigpiodaemon
        self.pi.set_mode(self.redPin, pigpio.OUTPUT)
        self.pi.set_mode(self.greenPin, pigpio.OUTPUT)
        self.pi.set_mode(self.bluePin, pigpio.OUTPUT)

    def off(self):
        self.pi.set_PWM_dutycycle(self.redPin, 0)
        self.pi.set_PWM_dutycycle(self.greenPin, 0)
        self.pi.set_PWM_dutycycle(self.bluePin, 0)

    def blink(self, color):
        self.pi.set_PWM_frequency(self.redPin, 10)
        self.pi.set_PWM_frequency(self.greenPin, 10)
        self.pi.set_PWM_frequency(self.bluePin, 10)

        self.pi.set_PWM_dutycycle(self.redPin, color[0] / 4)
        self.pi.set_PWM_dutycycle(self.greenPin, color[1] / 4)
        self.pi.set_PWM_dutycycle(self.bluePin, color[2] / 4)

    def on(self, color):
        self.pi.set_PWM_frequency(self.redPin, 200)
        self.pi.set_PWM_frequency(self.greenPin, 200)
        self.pi.set_PWM_frequency(self.bluePin, 200)

        self.pi.set_PWM_dutycycle(self.redPin, color[0])
        self.pi.set_PWM_dutycycle(self.greenPin, color[1])
        self.pi.set_PWM_dutycycle(self.bluePin, color[2])


class Pump:
    def __init__(self, fwdpin, bkwpin, leftencoder, rightencoder, pigpiodaemon):
        self.counter = 0
        self.fwdpin = fwdpin
        self.bkwpin = bkwpin

        self.leftEncoderPin = leftencoder
        self.rightEncoderPin = rightencoder
        self.leftEncoderLevel = 0
        self.rightEncoderLevel = 0
        self.lastActivated = None

        self.pi = pigpiodaemon
        self.pi.set_mode(self.fwdpin, pigpio.OUTPUT)
        self.pi.set_mode(self.bkwpin, pigpio.OUTPUT)

        self.pi.set_mode(self.leftEncoderPin, pigpio.INPUT)
        self.pi.set_mode(self.rightEncoderPin, pigpio.INPUT)

        self.pi.set_PWM_frequency(self.fwdpin, 200)
        self.pi.set_PWM_frequency(self.bkwpin, 200)
        self.pi.set_PWM_dutycycle(self.bkwpin, 0)
        self.pi.set_PWM_dutycycle(self.fwdpin, 0)

        self.pi.callback(self.leftEncoderPin, pigpio.EITHER_EDGE, self.transitionOccurred)
        self.pi.callback(self.rightEncoderPin, pigpio.EITHER_EDGE, self.transitionOccurred)

        self.delivering = False

        self.stepsForTurn = 700
        self.UlForTurn = 6
        self.stepsForUl = int(self.stepsForTurn / self.UlForTurn)

        self._killer = False

    def deliver(self, volume, speed):
        if volume != 0:
            previouserror = None
            static = 0
            while static < 5:
                error = (volume / 1000) * self.stepsForUl - self.counter
                if error < 5 and error > -5:
                    static += 1
                    print(static)
                updatedspeed = error * 0.045
                if updatedspeed < 0:
                    updatedspeed = min(updatedspeed, -100)
                    updatedspeed = max(-255, updatedspeed)
                    self.pi.set_PWM_dutycycle(self.bkwpin, -updatedspeed)
                    self.pi.set_PWM_dutycycle(self.fwdpin, 0)

                else:
                    updatedspeed = max(updatedspeed, 100)
                    updatedspeed = min(255, updatedspeed)
                    self.pi.set_PWM_dutycycle(self.fwdpin, updatedspeed)
                    self.pi.set_PWM_dutycycle(self.bkwpin, 0)

                if self._killer:
                    break
        else:
            while True:
                if self._killer:
                    print('here')
                    break
        self.pi.set_PWM_dutycycle(self.bkwpin, 0)
        self.pi.set_PWM_dutycycle(self.fwdpin, 0)


        self.counter = 0
        self.delivering = False

    def do_deliver(self, volume, speed):
        self._killer = False
        self.delivering = True
        self.o = Thread(target=self.deliver, args=(volume, speed))
        self.o.daemon = True
        self.o.start()

    def stop(self):
        self._killer = True
        self.o.join()

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

        if _gpio == self.leftEncoderPin:
            self.leftEncoderLevel = _level
        else:
            self.rightEncoderLevel = _level

        if _gpio != self.lastActivated:  # debounce
            self.lastActivated = _gpio

            if _gpio == self.leftEncoderPin and _level == 1:
                if self.rightEncoderLevel == 1:
                    self.counter += 1
            elif _gpio == self.rightEncoderPin and _level == 1:
                if self.leftEncoderLevel == 1:
                    self.counter -= 1

class Feeder:
    def __init__(self, deliverPump0, deliverPump1, waterPump, emptyPump):
        self.full = False
        self.cleaned = False
        self.filling = False
        self.when_filled = None
        self.when_emptied = -60

        self.deliverPump0 = deliverPump0
        self.deliverPump1 = deliverPump1
        self.waterPump = waterPump
        self.emptyPump = emptyPump

        self.priming = False

        self.visitors = {}

    def do_flush(self, volume):
        self.emptyPump.deliver(volume=-volume, speed=255)
        self.full = False
        self.when_emptied = time.time()
        self.do_clean()

    def do_fill(self, pump, amount= None, speed=255):
        if self.cleaned:
            self.emptyPump.deliver(-12000,255)
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

    def clean(self):
        self.waterPump.deliver(12000,255)
        self.emptyPump.deliver(-21000,255)
        self.waterPump.deliver(9000,255)
        self.cleaned=True

    def do_clean(self):
        self.o = Thread(target=self.clean)
        self.o.daemon = True
        self.o.start()

    def prime(self):
        for i in range(5):
            print('filling pump 0')
            self.deliverPump0.deliver(20000,255)
            print('done')
            print('flushing')
            self.emptyPump.deliver(-25000,255)
            print('done')

            print('filling pump 1')
            self.deliverPump1.deliver(20000,255)
            print('done')
            print('flushing')
            self.emptyPump.deliver(-25000,255)
            print('done')

            print('filling waterPump')
            self.waterPump.deliver(20000,255)
            print('done')

            print('flushing')
            self.emptyPump.deliver(-25000,255)
            print('done')
    def do_prime(self):
        self.o = Thread(target=self.prime)
        self.o.daemon = True
        self.o.start()
        
            



