import time
from connect import MQTT

expName = 'testingFlowers'


def decode(command):
    code = command[0:2]
    if code == '-h':
        print('available codes:')
        print('-a    Activate flowers    Use this command to turn on flowers. Arguments available')
        print('                          are "all" to turn on everything, or specify the single')
        print('                          flower names separated by a comma')
        print('-l    Learn mode flowers  Use this command to turn on learning mode on flowers. A60rguments available')
        print('                          are "all" to turn on everything, or specify the single')
        print('                          flower names separated by a comma')
        print('-k    Deactivate flowers  Use this command to turn off flowers. Arguments available')
        print('                          are "all" to turn on everything, or specify the single')
        print('                          flower names separated by a comma')
        print('-q    Quit                quit this software')
        return ['h','h']

    if code == '-a':
        if command[2:] == '':
            return ['wakeup', ['all']]
        else:
            return ['wakeup', command[3:].split(',')]
    elif code == '-p':
        if command[2:] == '':
            return ['prime', ['all']]
        else:
            return ['prime', command[3:].split(',')]
    elif code == '-k':
        if command[2:] == '':
            return ['kill', ['all']]
        else:
            return ['kill', command[3:].split(',')]
    elif code == '-l':
        if command[2:] == '':
            return ['learn', ['all']]
        else:
            return ['learn', command[3:].split(',')]
    elif code == '-q':
        return ['q','q']

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
mqtt = MQTT(expName)

print('all set. Make sure the flowers are on with the red LED blinking')
time.sleep(5)

while True:
    command = input('Enter a command. Type "-h" for available comments')
    message, receivers = decode(command)
    if message == 'q':
        break
    else:
        for receiver in receivers:
            mqtt.send('commands', message, receiver=receiver)

