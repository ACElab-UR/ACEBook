from paho.mqtt.client import Client  # # Python implementation of the MQTT protocol
import yaml
import time

with open(r'config.yaml') as file:  # open the config.yaml file in read mode and assign it to the variable "file"
    config = yaml.load(file, Loader=yaml.FullLoader)


# define a MQTT class that initializes the MQTT client and subscribes to different MQTT topics:
class MQTT:
    def __init__(self):
        self.myname = config['flowerID']  # take the info of the name of the flower from the config YAML
        self.port = 1883
        self.colors = config['colors']  # idem with colors
        self.client = Client(client_id=self.myname)  # this line creates an instance of the Client class from the
        # paho.mqtt.client module. It sets the client ID of the MQTT client to self.myname which is 'flowerID'

        # callback functions for when the flower connects or disconnects from the MQTT broker, or receive messages:
        self.client.on_connect = self.on_connect  # callback: The on_connect function will be called when the client
        # (= the flower) successfully connects to the MQTT broker
        self.client.on_disconnect = self.on_disconnect  # idem if disconnect
        self.client.on_message = self.on_message  # the on_message function will be called when the flower receives
        # a message from the MQTT broker

        self.Connected = False  # this variable represents the connection status of the flower
        self.client.connect(config['hubIP'])  # this line establishes the connection between the flower and the HUB

        self.client.loop_start()  # this line starts a background thread that listens for incoming messages from the
        # HUB

        while self.Connected != True:  # wait for connection
            time.sleep(0.1)

        # subscribe the flowers to the following topics:
        self.client.subscribe('commands')
        self.client.subscribe('contents')
        self.client.subscribe('rewards')

        # initializes instances for the flowers:
        self.last_message_received = None
        self.got_wakeup_message = False
        self.got_kill_message = False
        self.got_prime_message = False
        self.got_learn_message = False
        
        self.gotrewards = False
        self.gotcontents = False

        self.qualities = [0, 0]  # to track the quality of pumps 1 and 2
        self.scents = [0, 0]  # idem with odours

        self.rewardpatterns = {}

    # called when the flowers establish a connection to the HUB:
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            self.client.subscribe('commands')  # now flower subscribes to topics when it connects to MQTT
            self.client.subscribe('contents')
            self.client.subscribe('rewards')
            self.Connected = True  # Use global variable
        else:
            print("Connection failed")

    # this "on_disconnect" function is a callback function that is called when the client disconnects from the
    # MQTT broker. It tries to reconnect to the broker until the connection is established successfully:
    def on_disconnect(self, client, rc, props):
        self.Connected = False
        while not self.Connected:  # Wait for connection
            try:
                client.reconnect()
                self.Connected = True
            except ConnectionRefusedError:
                time.sleep(1)

    # define the on_message function of the MQTT class, called when a message is received on a subscribed topic:
    def on_message(self, client, userdata, message):
        load = str(message.payload.decode("utf-8"))
        topic = str(message.topic)
        timestamp = load.split('.')[0]
        sender = load.split('.')[1]
        receiver = load.split('.')[2]
        mess = load.split('.')[3]
        self.last_message_received = {'topic': topic, 'sender': sender, 'receiver': receiver, 'message': mess}
        self.decode()

    # this function "decode" decodes and handles incoming messages based on their topic and content:
    def decode(self):
        receiver = self.last_message_received['receiver']
        topic = self.last_message_received['topic']
        if receiver == 'all' or receiver == self.myname:
            if topic == 'commands':
                command = self.last_message_received['message']
                self.do(command)
            if topic == 'contents':
                vals = self.last_message_received['message'].split(',')
                print(vals)
                self.qualities = [int(vals[0]), int(vals[1])]
                self.scents = [vals[2], vals[3]]
                self.color = vals[4]
                mess = 'my pump 0 contains '+str(self.qualities[0])+' '+str(self.scents[0])
                self.send('debug', mess)
                mess = 'my pump 1 contains ' + str(self.qualities[1]) + ' ' + str(self.scents[1])
                self.send('debug', mess)
                self.gotcontents = True
            if topic == 'rewards':
                rewardpattern = int(self.last_message_received['message'].split(',')[0])
                self.rewardpatterns[rewardpattern] = {}
                self.rewardpatterns[rewardpattern]['bees'] = \
                    self.last_message_received['message'].split(',')[1].split('-')
                self.rewardpatterns[rewardpattern]['bees'] = \
                    [int(bee) for bee in self.rewardpatterns[rewardpattern]['bees']]

                quality = int(self.last_message_received['message'].split(',')[2])
                amount = int(self.last_message_received['message'].split(',')[3])
                scent = self.last_message_received['message'].split(',')[4]
                retention = int(self.last_message_received['message'].split(',')[5])

                self.rewardpatterns[rewardpattern]['amount'] = amount
                self.rewardpatterns[rewardpattern]['retention'] = retention
                self.rewardpatterns[rewardpattern]['quality'] = quality
                self.rewardpatterns[rewardpattern]['scent'] = scent
                if quality == self.qualities[0] and scent == self.scents[0]:
                    self.rewardpatterns[rewardpattern]['pump'] = 0
                    self.send('debug', 'reward pattern '+str(rewardpattern)+' associated with pump 0')
                elif quality == self.qualities[1] and scent == self.scents[1]:
                    self.rewardpatterns[rewardpattern]['pump'] = 1
                    self.send('debug', 'reward pattern '+str(rewardpattern)+' associated with pump 1')
                else:
                    self.send('debug', 'cannot find the correct pump')
                self.gotrewards = True
                print(self.rewardpatterns[rewardpattern])

        else:
            pass  # not for me

    def do(self, command):
        if command == 'wakeup':
            self.got_wakeup_message = True
            self.got_kill_message = False
            self.send('commands', 'turnedon')
        elif command == 'kill':
            self.got_kill_message = True
            self.got_wakeup_message = False
            self.send('commands', 'turnedoff')
        if command == 'check':
            self.send('commands', 'stillhere')
        elif command == 'prime':
            self.got_prime_message = True
            self.send('commands', 'received')
        elif command == 'learn':
            self.got_learn_message = True
            self.send('commands', 'received')

    def send(self, topic, message, receiver='HUB'):
        load = str(time.ctime())+'.'+self.myname+'.'+receiver+'.'+message
        self.client.publish(topic=topic, payload=load)
        print(load)
