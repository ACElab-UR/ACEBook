import camera
import electronics
from connect import MQTT
import routines

cam = camera.Cam()
markers = camera.Markers()

# creates a new instance of the "Feeder" class from electronics:
# each pump is associated with the pins controlling its motor's forward and backward directions, and with the pins to
# read the encoder signals (Clk = left; DT = right). electronics.pi refers to the pigpio daemon object used to control
# the GPIO pins on the Raspberry Pi:
feeder = electronics.Feeder(electronics.Pump(electronics.pins['motor1fwd'], electronics.pins['motor1bkw'],
                                             electronics.pins['motorClk1'], electronics.pins['motorDt1'],
                                             electronics.pi, UlForTurn=5.6),
                            electronics.Pump(electronics.pins['motor2fwd'], electronics.pins['motor2bkw'],
                                             electronics.pins['motorClk2'], electronics.pins['motorDt2'],
                                             electronics.pi, UlForTurn=5.7),
                            electronics.Pump(electronics.pins['motor3fwd'], electronics.pins['motor3bkw'],
                                             electronics.pins['motorClk3'], electronics.pins['motorDt3'],
                                             electronics.pi, UlForTurn=5.3),
                            electronics.Pump(electronics.pins['motor4fwd'], electronics.pins['motor4bkw'],
                                             electronics.pins['motorClk4'], electronics.pins['motorDt4'],
                                             electronics.pi, UlForTurn=5.6))

# creates an instance of the colorLED class from the "Electronics" module. Pins arguments are for each RGB LED
# pin, and the pi object represents the Raspberry Pi:
led = electronics.colorLED(electronics.pins['redLed'], electronics.pins['greenLed'], electronics.pins['blueLed'],
                           electronics.pi)

mqtt = MQTT()  # creates an instance of the MQTT class from the "connect" module

# little routine to check whether the RGB LEDs work fine:
led.blink(mqtt.colors['green'], duration=2.0)
led.blink(mqtt.colors['blue'], duration=2.0)
led.blink(mqtt.colors['red'], duration=2.0)

# The experiment starts here:
while True:  # awaiting commands
    if mqtt.got_wakeup_message:
        mqtt.got_wakeup_message = False
        routines.experiment(mqtt, led, cam, markers, feeder)
    elif mqtt.got_prime_message:
        mqtt.got_prime_message = False
        feeder.do_prime()
    elif mqtt.got_learn_message:
        mqtt.got_learn_message = False
        routines.colonylearn(mqtt, led, cam, markers, feeder)
