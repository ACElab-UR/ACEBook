import camera
import electronics

markers = camera.Markers()  # needed, else there's an error


feeder = electronics.Feeder(electronics.Pump(electronics.pins['motor1fwd'], electronics.pins['motor1bkw'],
                                             electronics.pins['motorClk1'], electronics.pins['motorDt1'],
                                             electronics.pi, UlForTurn=6),
                            electronics.Pump(electronics.pins['motor2fwd'], electronics.pins['motor2bkw'],
                                             electronics.pins['motorClk2'], electronics.pins['motorDt2'],
                                             electronics.pi, UlForTurn=6),
                            electronics.Pump(electronics.pins['motor3fwd'], electronics.pins['motor3bkw'],
                                             electronics.pins['motorClk3'], electronics.pins['motorDt3'],
                                             electronics.pi, UlForTurn=6),
                            electronics.Pump(electronics.pins['motor4fwd'], electronics.pins['motor4bkw'],
                                             electronics.pins['motorClk4'], electronics.pins['motorDt4'],
                                             electronics.pi, UlForTurn=6))


led = electronics.colorLED(electronics.pins['redLed'], electronics.pins['greenLed'], electronics.pins['blueLed'],
                           electronics.pi)


