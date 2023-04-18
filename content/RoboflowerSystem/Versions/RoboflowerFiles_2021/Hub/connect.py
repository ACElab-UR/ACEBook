from paho.mqtt.client import Client
import time
import yaml

class MQTT:
    def __init__(self, expfolder):

        with open(expfolder+'/contents.yaml', 'r') as file:
            self.contents = yaml.load(file, Loader=yaml.FullLoader)
        with open(expfolder+'/flowerGroups.yaml', 'r') as file:
            self.flowerGroups = yaml.load(file, Loader=yaml.FullLoader)
        with open(expfolder+'/rewardPatterns.yaml', 'r') as file:
            self.rewardPatterns = yaml.load(file, Loader=yaml.FullLoader)


        self.myname = 'HUB'
        self.port = 1883

        self.client = Client(client_id=self.myname)

        self.client.on_connect = self.on_connect  # attach function to callback
        self.client.on_message = self.on_message

        self.Connected = False
        self.client.connect('192.168.0.2')

        self.client.loop_start()  # start the loop

        while self.Connected != True:  # Wait for connection
            time.sleep(0.1)

        self.client.subscribe('commands')
        self.client.subscribe('log')
        self.client.subscribe('debug')
        self.client.subscribe('contents')
        self.client.subscribe('rewards')

        self.logger = Logger()


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
        self.decode(topic, timestamp, sender, mess)

    def decode(self, topic, timestamp, sender, mess):
        if topic == 'log' or topic == 'debug':
            self.logger.log(topic, timestamp, sender, mess)
        elif topic == 'commands':
            if mess == 'awaits':
                receiver = sender
                if receiver in self.flowerGroups['A']:
                    yourgroup = 'A'
                if receiver in self.flowerGroups['B']:
                    yourgroup = 'B'
                if receiver in self.flowerGroups['C']:
                    yourgroup = 'C'
                if receiver in self.flowerGroups['D']:
                    yourgroup = 'D'
                mess = str(self.contents[yourgroup][1]['quality']) + ',' + \
                       str(self.contents[yourgroup][2]['quality']) + ',' + \
                       str(self.contents[yourgroup][1]['scent']) + ',' +\
                       str(self.contents[yourgroup][2]['scent']) + ',' +\
                    str(self.contents[yourgroup]['color'])
                self.send('contents', mess, receiver)
                for rewardPattern in self.rewardPatterns:
                    bees = ''
                    for bee in self.rewardPatterns[rewardPattern]['bees']:
                        bees = bees+str(bee)+'-'
                    bees = bees[:-1]
                    mess = str(rewardPattern)+','+ bees + ',' + \
                           str(self.rewardPatterns[rewardPattern][yourgroup]['quality'])+','+ \
                           str(self.rewardPatterns[rewardPattern][yourgroup]['quantity']) + ',' + \
                           str(self.rewardPatterns[rewardPattern][yourgroup]['scent']) + ',' + \
                           str(self.rewardPatterns[rewardPattern][yourgroup]['retention'])
                    self.send('rewards', mess, receiver)

    def send(self, topic, message, receiver='all'):
        load = str(time.ctime())+'.'+self.myname+'.'+receiver+'.'+message
        self.client.publish(topic=topic, payload=load)
        print(load)


class Logger:
    def __init__(self):
        self.logname = 'data/'+str(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()))+'.log'
        self.debugname = 'data/'+str(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()))+'.debug'

        with open(self.logname, 'w') as f:
            f.write('time,flower,id,pump,quality,scent,amount,event\n')

        with open(self.debugname, 'w') as f:
            f.write('time,flower,message\n')

    def log(self, topic, t, s, m):
        if topic == 'log':
            ID, pump, quality, scent, amount, event = m.split(',')
            with open(self.logname, 'a') as f:
                f.write(t+','+s+','+ID+','+pump+','+quality+','+scent+','+amount+','+event+'\n')
                print(t+','+s+','+ID+','+pump+','+quality+','+scent+','+amount+','+event)
        elif topic == 'debug':
            with open(self.debugname, 'a') as f:
                f.write(t + ',' + s + ',' + m + '\n')
                print(t + ',' + s + ',' + m)

