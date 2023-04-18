import camera
import Electronics
from connect import MQTT
import routines

cam = camera.Cam()
markers = camera.Markers()

feeder = Electronics.Feeder(Electronics.Pump(Electronics.pins['motor1fwd'], Electronics.pins['motor1bkw'],
                                             Electronics.pins['motorClk1'], Electronics.pins['motorDt1'], Electronics.pi),
                            Electronics.Pump(Electronics.pins['motor2fwd'], Electronics.pins['motor2bkw'],
                                             Electronics.pins['motorClk2'], Electronics.pins['motorDt2'], Electronics.pi),
                            Electronics.Pump(Electronics.pins['motor3fwd'], Electronics.pins['motor3bkw'],
                                             Electronics.pins['motorClk3'], Electronics.pins['motorDt3'], Electronics.pi),
                            Electronics.Pump(Electronics.pins['motor4fwd'], Electronics.pins['motor4bkw'],
                                             Electronics.pins['motorClk4'], Electronics.pins['motorDt4'], Electronics.pi))

led = Electronics.colorLED(Electronics.pins['redLed'], Electronics.pins['greenLed'], Electronics.pins['blueLed'], Electronics.pi)

mqtt = MQTT()

led.blink(mqtt.colors['red'])


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


