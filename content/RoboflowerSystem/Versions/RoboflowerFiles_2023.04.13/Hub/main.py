import time
from connect import MQTT

expName = 'April2023'  # creates a variable expName with the string value 'exp_name'


# First we define the "decode" function which sets up the manual input to send orders to the flowers:
def decode(command):
    action = command[0]  # action is defined by the first letter typed in the input later in the script
    if command[2:] == '':
        arguments = ['all']  # if no arguments, the argument is "all" by default
    else:
        arguments = command[2:].split(',')  # if arguments, split them by commas

    if action == 'h':  # gives comments for each possible action
        print('available actions:')
        print('a    Activate flowers    Use this command to turn on flowers. Arguments available')
        print('                          are "all" to turn on everything, or specify the single')
        print('                          flower names separated by a comma')
        print('l    Learn mode flowers  Use this command to turn on learning mode on flowers. Arguments available')
        print('                          are "all" to turn on everything, or specify the single')
        print('                          flower names separated by a comma')
        print('p    Prime flowers  Use this command to do a priming routine for the pumps. Arguments available')
        print('                          are "all" to prime everything, or specify the single')
        print('                          flower names separated by a comma')
        print('k    Deactivate flowers  Use this command to turn off flowers. Arguments available')
        print('                          are "all" to turn on everything, or specify the single')
        print('                          flower names separated by a comma')
        print('q    Quit                quit this software')
        return ['h', 'h']

    if action == 'a':
        return ['wakeup', arguments]
    elif action == 'p':
        return ['prime', arguments]
    elif action == 'k':
        return ['kill', arguments]
    elif action == 'l':
        return ['learn', arguments]
    elif action == 'q':
        return ['quit', 'q']
    else:
        print('code not recognized')


# Code starts here! Wait to receive commands from user and sends them to the flowers via MQTT:
print("""
____________________________________________________________
|                                                          |
|      _____  _________ ___________.__        ___.         |
|     /  _  \ \_   ___ \\\_   _____/|  | _____ \_ |__       |
|    /  /_\  \/    \  \/ |    __)_ |  | \__  \ | __ \      |
|   /    |    \     \____|        \|  |__/ __ \| \_\ \\     |
|   \____|__  /\______  /_______  /|____(____  /___  /     |
|           \/        \/        \/           \/    \/      |
|                                                          |
|__________________________________________________________| 

""")
print('Welcome to the artificial flower software')

print('Make sure that the mosquitto server is up and running')
mqtt = MQTT(expName)  # creates an instance of the MQTT class from the "connect" module with the experiment name
# passed as a parameter. This instance will be used to connect to the MQTT broker and communicate with the flowers

print('All set! Make sure the flowers are on with the red LED blinking')
time.sleep(5)

# keeps running the "keepchecking" method of the MQTT class in the background to check for new messages:
mqtt.do_keepchecking()

# Infinite loop that reads the actions the user specifies in the console, and send the actions to all the receivers:
while True:
    command = input('Enter a command. Type "h" for available actions: ')  # prompts the user to enter a command and
    # assigns the user input to the command variable, defined earlier in the "decode" function
    message, receivers = decode(command)
    if message == 'q':
        break
    else:
        for receiver in receivers:  # send command to all receivers (= flowers) via the MQTT broker
            mqtt.send('commands', message, receiver=receiver)
