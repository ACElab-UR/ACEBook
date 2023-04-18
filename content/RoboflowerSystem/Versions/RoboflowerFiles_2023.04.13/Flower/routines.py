import datetime
import time
import cv2  # library mainly aimed at real-time computer vision
# note: these functions are just defined in this module, and do not import any class or function from other modules


# the function experiment takes in 5 parameters: mqtt, led, cam, markers, and feeder
def experiment(mqtt, led, cam, markers, feeder):
    # sends a message "I woke up" under "debug" using the send method of the mqtt parameter:
    mqtt.send('debug', 'I woke up!')
    led.blink(mqtt.colors['green'], duration=2.0)  # blink the RGB LEDs for 2sec
    # sends the message "awaits" under the "commands" topic
    mqtt.send('commands', 'awaits')
    #  waits until the mqtt object receives data for both the contents and rewards channels:
    while not (mqtt.gotcontents and mqtt.gotrewards):
        pass
    led.on(mqtt.colors[mqtt.color])  # turns on the LED with the corresponding color
    print("the colour of the flower is " + mqtt.color)  # prints the current color of the flower

    cam.start()  # starts the camera by calling the start method of the cam object
    time.sleep(2)

    # send messages under the topics debug and log:
    mqtt.send('debug', 'camera started')
    mqtt.send('debug', 'save this time as: ')
    mqtt.send('log', 'NA,NA,NA,NA,NA,started')

    # creates an empty dictionary called thisbee with 3 keys: id, pump and amount
    thisbee = {'id: ': None, 'pump: ': None, 'amount: ': None}
    feeder.do_clean()
    # does a cleaning routine (pump 3 = +12uL, pump 4= -21uL, pump 3 = +9uL)

    while True:
        now = time.time()  # gets the current time in seconds and assigns it to the variable "now"
        frame = cam.grab()  # grabs a frame from the camera and assigns it to the variable "frame"
        markers.detect(frame)  # detects the markers in the current frame using the marker detection algorithm
        # cv2.imshow('f', frame)
        # cv2.waitKey(1)

        # if a bee has arrived at the feeder:
        if markers.bee_arrived:
            # it sends a message to the "log" channel of the MQTT broker indicating that a bee has arrived:
            mqtt.send('log', str(markers.last_seen) + ',NA,NA,NA,NA,bee arrived')
            markers.bee_arrived = False

        # if a bee has left the feeder:
        if markers.bee_gone:
            mqtt.send('log', str(markers.last_seen) + ',NA,NA,NA,NA,bee gone')
            markers.bee_gone = False

        # if the camera is currently detecting a marker (markers.being_seen) and the detected markers.ID is not None
        # and the marker has not already been recognized (not markers.beenRecognized:
        if markers.being_seen and markers.IDs is not None and not markers.beenRecognized:
            # calls the recognize() method of the markers object, which takes in the rewardpatterns dictionary and
            # returns the reward pattern that matches the detected marker ID and assigns it to "thisbeepattern":
            thisbeepattern = markers.recognize(mqtt.rewardpatterns)

            # if the bee has not yet been recognized in this experiment session:
            if not markers.beenRecognized:
                if str(markers.IDs[0][0]) not in (x[1] for x in markers.beenNotified):
                    mqtt.send('debug', 'seen a marker not expected: ' + str(markers.IDs[0][0]))
                    # if the ID is not already in the list of IDs, sends a debug message:
                    markers.beenNotified.append((now, str(markers.IDs[0][0])))

                # if the time elapsed since the bee was detected is greater than 30 seconds,
                # remove the bee's ID and detection time from the list of detected but not expected bees:
                for t in list(markers.beenNotified):
                    if now-t[0] > 30:
                        markers.beenNotified.remove(t)

            # if the bee has already been recognized previously in the experiment session:
            elif markers.beenRecognized:
                ID = markers.IDs[0][0]
                # send a debug message to the MQTT broker indicating that a bee with the given ID has been seen:
                mqtt.send('debug', 'seen a  marker: ' + str(ID))
                lastentered = ID

                # if the feeder is not full:
                if not feeder.full:
                    # if the ID of the bee is already in the visitors' dictionary of the feeder:
                    if ID in feeder.visitors:
                        # if the time elapsed since the last time the feeder was emptied for this bee ID is
                        # greater than the retention time (see MQTT reward pattern):
                        if time.time()-feeder.visitors[ID]['when_emptied'] > \
                                mqtt.rewardpatterns[thisbeepattern]['retention']:
                            # Update infos of the bee and the flower conditions to the according dictionaries:
                            thisbee['id'] = ID
                            thisbee['pump'] = mqtt.rewardpatterns[thisbeepattern]['pump']
                            thisbee['amount'] = mqtt.rewardpatterns[thisbeepattern]['amount']
                            thisbee['quality'] = mqtt.rewardpatterns[thisbeepattern]['quality']
                            thisbee['scent'] = mqtt.rewardpatterns[thisbeepattern]['scent']

                            feeder.do_fill(thisbee['pump'], amount=thisbee['amount'])

                            mqtt.send('debug', 'giving to bee ' + str(thisbee['id']) + ' solution from pump '
                                      + str(thisbee['pump']) + ' of quality ' + str(thisbee['quality']/1000) + ' M '
                                      + str(thisbee['scent']) + ' for ' + str(thisbee['amount']/1000) + ' ul')

                            mqtt.send('log', str(thisbee['id']) + ',' + str(thisbee['pump']) + ',' + str(
                                thisbee['quality']) + ',' + str(thisbee['scent']) + ',' + str(
                                thisbee['amount']) + ',' + 'filling')

                            # updates the when_filled key of the feeder.visitors[ID] dictionary with current time:
                            feeder.visitors[ID]['when_filled'] = time.time()

                        # if the time elapsed since the last time the feeder was emptied for this bee ID is
                        # smaller than the retention time, send the info to debug and log:
                        else:
                            mqtt.send('debug', 'I have seen ' + str(ID) + ' but the retention time has not elapsed')
                            mqtt.send('log', str(ID) + ',NA,NA,NA,NA,retention')

                    # if the ID of the bee is not already in the visitors' dictionary of the feeder:
                    else:
                        thisbee['id'] = ID
                        thisbee['pump'] = mqtt.rewardpatterns[thisbeepattern]['pump']
                        thisbee['amount'] = mqtt.rewardpatterns[thisbeepattern]['amount']
                        thisbee['quality'] = mqtt.rewardpatterns[thisbeepattern]['quality']
                        thisbee['scent'] = mqtt.rewardpatterns[thisbeepattern]['scent']

                        feeder.do_fill(thisbee['pump'], amount=thisbee['amount'])

                        mqtt.send('debug', 'giving to bee ' + str(thisbee['id']) + ' solution from pump ' + str(
                            thisbee['pump']) + ' of quality ' + str(thisbee['quality']/1000) + ' M ' + str(
                            thisbee['scent']) + ' for ' + str(thisbee['amount']/1000) + ' ul')

                        mqtt.send('log', str(thisbee['id']) + ',' + str(thisbee['pump']) + ',' + str(
                            thisbee['quality']) + ',' + str(thisbee['scent']) + ',' + str(
                            thisbee['amount']) + ',' + 'filling')

                        feeder.visitors[ID] = {'when_filled': time.time(), 'when_emptied': None}

                # if the feeder is already full, send the info to debug and log:
                elif feeder.full:
                    mqtt.send('debug', 'the feeder is full already')
                    mqtt.send('log', str(ID)+',NA,NA,NA,NA,feeder full')

        # if there is no marker currently being seen by the camera:
        elif not markers.being_seen:
            # and if the feeder is full:
            if feeder.full:
                # checks whether the time elapsed since the last filling is greater than 60 seconds:
                if time.time()-feeder.visitors[thisbee['id']]['when_filled'] > 60:
                    # send to debug and log that there is no bee and the feeder is being emptied:
                    mqtt.send('debug', 'no bee, emptying the feeder')
                    mqtt.send('log', 'NA,NA,NA,NA,NA,empty')
                    feeder.do_flush(80000)  # pump 4 flushes 80uL (wow it's a lot)
                    # sets the time when the feeder was emptied in the "feeder.visitors" dictionary:
                    feeder.visitors[thisbee['id']]['when_emptied'] = time.time()

        # if received a "prime" instruction from mqtt:
        if mqtt.got_prime_message:
            # do the priming routine:
            feeder.do_prime()
            mqtt.got_prime_message = False

        # if received a "kill" instruction from mqtt, send the info to debug and log, turn off LEDs and exit
        # the "experiment" function:
        if mqtt.got_kill_message:
            mqtt.send('debug', 'I got turned off :( Goodnight!')
            mqtt.send('log', 'NA,NA,NA,NA,NA,quit')
            led.off()
            break


# the "colonylearn" function carries out the main routine of the automated flowers, but in learning mode:
def colonylearn(mqtt, led, cam, markers, feeder):
    seenmarkers = []
    mqtt.send('debug', 'I woke up in learning mode')  # send the info to debug only that flowers are in learning mode
    led.off()  # turns off the LEDs
    mqtt.send('commands', 'awaits')  # waits for commands from MQTT (but doesn't really - it's learning mode,
    # there is no info to receive for an experiment

    mqtt.send('debug', 'camera started')
    mqtt.send('debug', 'save this time as 0')
    mqtt.send('log', 'NA,NA,NA,NA,NA,LearnStarted')
    thisbee = {'id': None, 'pump': None, 'amount': None}
    
    cam.start()
    time.sleep(2)

    while True:
        frame = cam.grab()  # grabs a frame from the camera and assigns it to the variable "frame"
        markers.detect(frame)  # detects the markers in the current frame using the marker detection algorithm
        cv2.waitKey(1)  # necessary to ensure that the window is updated and remains responsive

        if markers.being_seen and markers.IDs is not None and not markers.beenRecognized:
            markers.beenRecognized = True
            ID = markers.IDs[0][0]
            seenmarkers.append(ID)
            # sends a debug message via MQTT indicating that a marker with the given ID has been seen:
            mqtt.send('debug', 'seen a  marker: ' + str(ID))

            # if the feeder is not full:
            if not feeder.full:
                # if more than 60 seconds have passed since the last time the feeder was emptied:
                if time.time()-feeder.when_emptied > 60:
                    thisbee['id'] = ID
                    thisbee['pump'] = 0  # pump 1
                    thisbee['amount'] = 50000  # 50uL of sucrose (so completely full!)
                    thisbee['quality'] = 'null'
                    thisbee['scent'] = 'null'
                    print("bee " + str(ID) + " receives " + str(thisbee['amount']/1000) + " ul of sucrose")

                    # fills the feeder with sugar (from pump 1, 50uL) using the do_fill method of the feeder object:
                    feeder.do_fill(thisbee['pump'], amount=thisbee['amount'])
                    # send the info to debug and log:
                    mqtt.send('debug', 'giving to bee ' + str(thisbee['id']) + ' solution from pump '
                              + str(thisbee['pump']) + ' of quality ' + str(thisbee['quality']) + ' M '
                              + str(thisbee['scent']) + ' for ' + str(thisbee['amount']/1000) + ' ul')

                    mqtt.send('log', str(thisbee['id']) + ',' + str(thisbee['pump']) + ',' +
                              (thisbee['quality']) + ',' + (thisbee['scent']) + ','
                              + str(thisbee['amount']) + ',' + 'filling')

                # if the feeder is not full and less than 60 seconds have passed since the feeder was last emptied:
                else:
                    mqtt.send('debug', 'I have seen ' + str(ID) + ' but the retention time has not elapsed')
                    mqtt.send('log', str(ID) + ',NA,NA,NA,NA,retention')

            # if the feeder is full:
            elif feeder.full:
                mqtt.send('debug', 'the feeder is already full')

        # if no marker is being seen and if the feeder is full, empty it:
        elif not markers.being_seen:
            if feeder.full:
                mqtt.send('debug', 'no bee: emptying the feeder')
                feeder.do_flush(100000)  # flush out 100uL

        # if receive a prime message, do priming routine:
        if mqtt.got_prime_message:
            feeder.do_prime()
            mqtt.got_prime_message = False

        # if receive a kill message, send info to debug and log and break from the colonylearn function:
        if mqtt.got_kill_message:
            mqtt.send('debug', 'I got turned off :( Goodnight!')
            mqtt.send('debug', 'in the end I have seen today: ' + str(seenmarkers))
            mqtt.send('log', 'NA,NA,NA,NA,NA,quit')
            break
