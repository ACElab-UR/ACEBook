import time
from connect import MQTT

expName = 'Test10-22'


# this function is the manual input to send orders to the flowers
def decode(command):
    action = command[0:1]  # first letter is the action (a, p, k...)
    arguments = command[2:].split(',')  # rest is argument such as flower name, or "all"
    if arguments == '':
        arguments = ['all']  # if no arguments, then send "all" by default!

    if action == 'h':
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
        return ['q', 'q']
    else:
        print('code not recognized')

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

mqtt.do_keepchecking()
while True:
    command = input('Enter a command. Type "h" for available comments')
    message, receivers = decode(command)
    if message == 'q':
        break
    else:
        for receiver in receivers:  # send topics to receivers (= flowers!)
            mqtt.send('commands', message, receiver=receiver)
