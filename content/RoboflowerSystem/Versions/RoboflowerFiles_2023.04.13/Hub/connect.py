from paho.mqtt.client import Client  # # The Client class is used to publish and subscribe to MQTT messages
import time  # handles time-related tasks
import yaml  # human-friendly file format to read data easily
from threading import Thread, Event  # used to perform multiple tasks simultaneously


# this MQTT class allows the communication between the HUB and the roboflowers
class MQTT:
    def __init__(self, exp_folder):  # takes as argument "exp_folder" which contains the YAML configuration files

        # opens in read mode the 3 YAML files and stores the contents in distinct variables:
        with open(exp_folder + '/contents.yaml', 'r') as file:
            self.contents = yaml.load(file, Loader=yaml.FullLoader)  # "contents" variable
        with open(exp_folder + '/flowerGroups.yaml', 'r') as file:
            self.flowerGroups = yaml.load(file, Loader=yaml.FullLoader)  # "flowerGroups" variable
        with open(exp_folder + '/rewardPatterns.yaml', 'r') as file:
            self.rewardPatterns = yaml.load(file, Loader=yaml.FullLoader)  # "rewardPatterns" variable

        self.myname = 'HUB'  # assigns the name of MQTT object to "HUB"
        self.port = 1883  # sets the port attribute to the default MQTT port number
        self.client = Client(client_id=self.myname)  # using the built-in Client class from paho.mqtt; sets the
        # client_id parameter to "myname" = HUB

        # callback functions called when the MQTT class is instantiated:
        self.client.on_connect = self.on_connect  # on connect, execute this on_connect method of the client object
        self.client.on_disconnect = self.on_disconnect  # idem if disconnect
        self.client.on_message = self.on_message  # will be called when the flower receives a message from the broker

        self.Connected = False  # sets the Connected attribute of the MQTT object to False
        self.client.connect('192.168.0.2')  # built-in method of the client object that connects the client
        # to the broker that runs at this IP address
        self.client.loop_start()  # built-in method of the client object that starts a loop which listens to incoming
        # messages from the broker
        while self.Connected is not True:  # wait for connection
            time.sleep(0.1)

        # subscribe the HUB to the 'commands', 'contents', and 'rewards' topics on the broker like the Flower but also
        # to the "log" and "debug" topics; the HUB will receive any messages that are published to these topics
        self.client.subscribe('commands')
        self.client.subscribe('log')
        self.client.subscribe('debug')
        self.client.subscribe('contents')
        self.client.subscribe('rewards')

        # creates a Logger object (from class below) and assigns it to the logger attribute of the mqtt object:
        self.logger = Logger()
        self.ONflowers = []
        self.stillONflowers = []
        self.lastcheck = time.time()

    # The "on_connect " callback function is called automatically when the HUB connects to the broker:
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:  # the arguments of on_connect will be passed in automatically by the Paho MQTT client library
            # when the function is called as a callback
            print("Connected to broker")
            self.Connected = True  # the client is now connected to the broker
        else:
            print("Connection failed")

    # The "on_disconnect" callback function is called when the HUB disconnects from the MQTT broker
    def on_disconnect(self, client, userdata, rc):
        print('Disconnected from broker. Trying to reconnect...')
        self.Connected = False
        while not self.Connected:  # Wait for connection
            try:
                client.reconnect()  # tries to reconnect to the broker until the connection is established successfully
                self.Connected = True
            except ConnectionRefusedError:
                time.sleep(1)

    # the "on_message" callback function is called when a message is received on a subscribed topic:
    def on_message(self, client, userdata, message):
        # decodes the payload of the message which is a string in the format sender.receiver.message:
        load = str(message.payload.decode("utf-8"))
        topic = str(message.topic)
        timestamp = str(time.ctime())
        # extracts the sender, receiver, and message parts of load, and stores them variables:
        sender = load.split('.')[1]
        receiver = load.split('.')[2]
        mess = load.split('.')[3]
        # The decode() method interprets the message and performs the appropriate action on the flowers:
        self.decode(topic, timestamp, sender, mess)

    # this function "decode" decodes and handles incoming messages based on their topic and content:
    def decode(self, topic, timestamp, sender, mess):
        # checks whether the incoming message topic is 'log' or 'debug':
        if topic == 'log' or topic == 'debug':
            self.logger.log(topic, timestamp, sender, mess)  # calls the log method of the logger object (see below)
        elif topic == 'commands':
            if mess == 'turnedon':
                self.ONflowers.append(sender)
            if mess == 'turnedoff':
                self.ONflowers.remove(sender)
            if mess == 'stillhere':
                self.stillONflowers.append(sender)
                print(sender, ': still here')
            if mess == 'awaits':
                receiver = sender
                # check which flower group the receiver belongs to and set the group accordingly:
                if receiver in self.flowerGroups['A']:
                    yourgroup = 'A'
                if receiver in self.flowerGroups['B']:
                    yourgroup = 'B'
                if receiver in self.flowerGroups['C']:
                    yourgroup = 'C'
                if receiver in self.flowerGroups['D']:
                    yourgroup = 'D'
                # generates a message containing the reward pattern and sends it to the receiver:
                mess = str(self.contents[yourgroup][1]['quality']) + ',' + \
                    str(self.contents[yourgroup][2]['quality']) + ',' + \
                    str(self.contents[yourgroup][1]['scent']) + ',' + \
                    str(self.contents[yourgroup][2]['scent']) + ',' + \
                    str(self.contents[yourgroup]['color'])
                self.send('contents', mess, receiver)  # sends the "mess" to the flower through MQTT with the topic
                # 'contents'
                # iterates through the lines of the rewardPatterns YAML file:
                for rewardPattern in self.rewardPatterns:
                    bees = ''  # creates an empty "bees" variable
                    # iterates through the "bees" in the current reward pattern:
                    for bee in self.rewardPatterns[rewardPattern]['bees']:
                        bees = bees + str(bee) + '-'  # appends the ID of each bee (separated by -) to the "bees" string
                    bees = bees[:-1]  # removes the last hyphen from the bees string
                    mess = str(rewardPattern) + ',' + bees + ',' + \
                        str(self.rewardPatterns[rewardPattern][yourgroup]['quality']) + ',' + \
                        str(self.rewardPatterns[rewardPattern][yourgroup]['quantity']) + ',' + \
                        str(self.rewardPatterns[rewardPattern][yourgroup]['scent']) + ',' + \
                        str(self.rewardPatterns[rewardPattern][yourgroup]['retention'])
                    self.send('rewards', mess, receiver)

    # the send method takes three arguments: topic, message, and receiver = all:
    def send(self, topic, message, receiver='all'):
        # creates a string variable "load" in the format: current time: HUB receiver message
        load = str(time.ctime()) + '.' + self.myname + '.' + receiver + '.' + message
        self.client.publish(topic=topic, payload=load)  # uses the "publish()" method to publish the load message to
        # the specified topic. The payload parameter is set to the load string that was created in the previous line
        print(load)  # this is the: "date - from HUB to all: check" that appears in the main of the HUB!

    # the "keepchecking" function runs in an infinite loop and checks every minute if the flowers are still connected:
    def keepchecking(self):
        while True:
            if len(self.ONflowers) > 0:  # if there is any flower in the "ONflowers" list:
                if time.time() - self.lastcheck > 60:  # if the last "check" is more than 1mn old:
                    self.send('commands', 'check')  # this sends a message to all connected flowers telling them to
                    # respond with a "still here" message
                    time.sleep(10)
                    # creates a list called "notanswered" that contains any flowers that did not respond with
                    # a "still here" message
                    notanswered = list(set(self.ONflowers).difference(set(self.stillONflowers)))
                    # if this list is not empty, send to the debug topic
                    if len(notanswered) > 0:
                        for dead in notanswered:
                            self.logger.log('debug', time.ctime(), dead,
                                            'flower ' + dead + ' is not responding anymore')
                    self.stillONflowers = []  # clears the "stillONflowers" list so that it can be used to track
                    # which flowers are still connected during the next iteration of the loop
                    self.lastcheck = time.time()  # updates the "lastcheck" variable with the current time
            if self._killer == True:  # checks if the _killer variable is True, indicating that the program should stop
                break  # ends the function

    # "do_keepchecking" is a method that sets up the thread that execute the keepchecking function (in the background):
    def do_keepchecking(self):
        self._killer = False  # sets _killer attribute to False, which is used to control when the thread should stop
        self.o = Thread(target=self.keepchecking)  # sets o as a new thread, with target set to keepchecking method.
        # sets it as a daemon thread meaning that if the main program terminates, this thread will also be terminated
        self.o.daemon = True
        self.o.start()

    # stops the continuous checking process initiated by the keepchecking method
    def stop(self):
        self._killer = True
        self.o.join()


# the class "Logger" generates the log and debug files. The log() method within the class writes to these files:
class Logger:
    def __init__(self):
        # generates two files for log and debug in the data directory, and their filename follow the following format:
        self.logname = 'data/' + str(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())) + '.log'
        self.debugname = 'data/' + str(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())) + '.debug'

        # opens the files in write mode and creates a header row with the following variables:
        with open(self.logname, 'w') as f:
            f.write('time,flower,id,pump,quality,scent,amount,event\n')
        with open(self.debugname, 'w') as f:
            f.write('time, flower, message\n')

    # the log method writes to the log and debug files. topic is either "log" or "debug":
    def log(self, topic, t, s, m):  # t = timestamp, s = sender and m = message
        if topic == 'log':
            # print(m)
            # extracts the ID, pump, quality, scent, amount, and event from the message (m) and split them by commas:
            ID, pump, quality, scent, amount, event = m.split(',')  # ID is the bee's aruco marker
            # opens the log file in append mode and writes a line of comma-separated values: timestamp, sender, and m:
            with open(self.logname, 'a') as f:
                f.write(t + ',' + s + ',' + ID + ',' + pump + ',' + quality + ',' + scent + ','
                        + amount + ',' + event + '\n')
                # prints the information to the console:
                print(t + ', ' + s + ', ' + 'bee ' + ID + ': ' + pump + ' gave ' + quality + ' M of ' + scent +
                      ' and ' + amount + ' uL' + ': ' + event)

        elif topic == 'debug':
            # opens the debug file in append mode and writes a line of comma-separated values to it consisting of:
            # timestamp, sender, and m
            with open(self.debugname, 'a') as f:
                f.write(t + ', ' + s + ', ' + m + '\n')
                print(t + ', ' + s + ': ' + m)
