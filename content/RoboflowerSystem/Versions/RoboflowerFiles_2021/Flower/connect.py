from paho.mqtt.client import Client
import yaml
import time

with open(r'config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class MQTT:
    def __init__(self):
        self.myname = config['flowerID']
        self.port = 1883
        self.colors = config['colors']

        self.client = Client(client_id=self.myname)

        self.client.on_connect = self.on_connect  # attach function to callback
        self.client.on_message = self.on_message

        self.Connected = False
        self.client.connect(config['hubIP'])

        self.client.loop_start()  # start the loop

        while self.Connected != True:  # Wait for connection
            time.sleep(0.1)

        self.client.subscribe('commands')
        self.client.subscribe('contents')
        self.client.subscribe('rewards')
                        
        self.last_message_received = None
        self.got_wakeup_message = False
        self.got_kill_message = False
        self.got_prime_message = False
        self.got_learn_message = False
        
        self.gotrewards = False
        self.gotcontents = False

        self.qualities= [0,0]
        self.scents = [0,0]

        self.rewardpatterns = {}

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            self.Connected = True  # Use global variable
        else:
            print("Connection failed")

    def on_message(self, client, userdata, message):
        load = str(message.payload.decode("utf-8"))
        topic = str(message.topic)
        timestamp = load.split('.')[0]
        sender = load.split('.')[1]
        receiver = load.split('.')[2]
        mess = load.split('.')[3]
        self.last_message_received = {'topic': topic, 'sender': sender,
                                      'receiver': receiver, 'message': mess}
        self.decode()

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
                self.rewardpatterns[rewardpattern]['bees'] = self.last_message_received['message'].split(',')[1].split('-')
                self.rewardpatterns[rewardpattern]['bees'] = [int(bee) for bee in self.rewardpatterns[rewardpattern]['bees']]

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
            pass #notforme

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
            self.send('commands','received')
        elif command == 'learn':
            self.got_learn_message = True
            self.send('commands','received')


    def send(self, topic, message, receiver='HUB'):
        load = str(time.ctime())+'.'+self.myname+'.'+receiver+'.'+message
        self.client.publish(topic=topic, payload=load)
        print(load)
