import time
import cv2


def experiment(mqtt, led, cam, markers, feeder):
    mqtt.send('debug', 'I woke up')

    led.blink(mqtt.colors['green'])

    mqtt.send('commands', 'awaits')

    while not (mqtt.gotcontents and mqtt.gotrewards):
        pass

    led.on(mqtt.colors[mqtt.color])
    print(mqtt.color)

    cam.start()
    time.sleep(2)
    mqtt.send('debug', 'Video started')

    mqtt.send('debug', 'Save this time as ')
    mqtt.send('log', 'NA,NA,NA,NA,NA,Started')

    thisbee = {'id': None, 'pump': None, 'amount': None}
    feeder.do_clean()

    while True:
        now = time.time()
        frame = cam.grab()
        markers.detect(frame)
        # cv2.imshow('f', frame)
        # cv2.waitKey(1)
        if markers.bee_arrived:
            mqtt.send('log', str(markers.last_seen)+',NA,NA,NA,NA,arrived')
            markers.bee_arrived = False
        if markers.bee_gone:
            mqtt.send('log', str(markers.last_seen)+',NA,NA,NA,NA,gone')
            markers.bee_gone = False
        if markers.being_seen and markers.IDs is not None and not markers.beenRecognized:
            thisbeepattern = markers.recognize(mqtt.rewardpatterns)
            if not markers.beenRecognized:
                if str(markers.IDs[0][0]) not in (x[1] for x in markers.beenNotified):
                    mqtt.send('debug', 'Seen a  marker not expected - ' + str(markers.IDs[0][0]))
                    markers.beenNotified.append((now, str(markers.IDs[0][0])))
                for t in list(markers.beenNotified):
                    if now-t[0] > 30:
                        markers.beenNotified.remove(t)                            
                
            elif markers.beenRecognized:
                ID = markers.IDs[0][0]
                mqtt.send('debug', 'Seen a  marker - ' + str(ID))
                lastentered = ID

                if not feeder.full:
                    if ID in feeder.visitors:
                        if time.time()-feeder.visitors[ID]['when_emptied'] > mqtt.rewardpatterns[thisbeepattern]['retention']:
                            thisbee['id'] = ID
                            thisbee['pump'] = mqtt.rewardpatterns[thisbeepattern]['pump']
                            thisbee['amount'] = mqtt.rewardpatterns[thisbeepattern]['amount']
                            thisbee['quality'] = mqtt.rewardpatterns[thisbeepattern]['quality']
                            thisbee['scent'] = mqtt.rewardpatterns[thisbeepattern]['scent']

                            feeder.do_fill(thisbee['pump'], amount=thisbee['amount'])
                            mqtt.send('debug', 'giving '+str(thisbee['id'])+' sugar from pump '+str(thisbee['pump']) +
                                      ' of quality '+str(thisbee['quality'])+'and scent '+str(thisbee['scent']) +
                                      ' for '+str(thisbee['amount']/1000)+'ul')
                            mqtt.send('log', str(thisbee['id'])+','+str(thisbee['pump'])+','+str(thisbee['quality']) +
                                      ','+str(thisbee['scent'])+','+str(thisbee['amount'])+',filling')
                            feeder.visitors[ID]['when_filled'] = time.time()
                        else:
                            mqtt.send('debug', 'i have seen '+str(ID)+' but the retention time has not elapsed')
                            mqtt.send('log', str(ID)+',NA,NA,NA,NA,retention')
                    else:
                        thisbee['id'] = ID
                        thisbee['pump'] = mqtt.rewardpatterns[thisbeepattern]['pump']
                        thisbee['amount'] = mqtt.rewardpatterns[thisbeepattern]['amount']
                        thisbee['quality'] = mqtt.rewardpatterns[thisbeepattern]['quality']
                        thisbee['scent'] = mqtt.rewardpatterns[thisbeepattern]['scent']

                        feeder.do_fill(thisbee['pump'], amount=thisbee['amount'])
                        mqtt.send('debug', 'giving ' + str(thisbee['id']) + ' sugar from pump ' + str(
                            thisbee['pump']) + ' of quality ' + str(thisbee['quality']) + 'and scent ' + str(
                            thisbee['scent']) + ' for ' + str(thisbee['amount'] / 1000) + 'ul')
                        mqtt.send('log', str(thisbee['id']) + ',' + str(thisbee['pump']) + ',' + str(
                            thisbee['quality']) + ',' + str(thisbee['scent']) + ',' + str(
                            thisbee['amount']) + ',filling')
                        feeder.visitors[ID] = {'when_filled': time.time(), 'when_emptied': None}
                elif feeder.full:
                    mqtt.send('debug', 'the feeder is full already')
                    mqtt.send('log', str(ID)+',NA,NA,NA,NA,full')
        elif not markers.being_seen:
            if feeder.full:
                if time.time()-feeder.visitors[thisbee['id']]['when_filled'] > 60:
                    mqtt.send('debug', 'no bee, emptying the feeder')
                    mqtt.send('log', 'NA,NA,NA,NA,NA,empty')
                    feeder.do_flush(80000)
                    feeder.visitors[thisbee['id']]['when_emptied']=time.time()
        if mqtt.got_prime_message:
            feeder.do_prime()
            mqtt.got_prime_message=False

        if mqtt.got_kill_message:
            mqtt.send('debug', 'I got turned off :( Goodnight!')
            mqtt.send('log', 'NA,NA,NA,NA,NA,Quit')
            led.off()
            break


def colonylearn(mqtt, led, cam, markers, feeder):
    seenmarkers = []
    mqtt.send('debug', 'I woke up in learn mode')

    led.off()

    mqtt.send('commands', 'awaits')

    cam.start()
    time.sleep(2)
    mqtt.send('debug', 'Video started')

    mqtt.send('debug', 'Save this time as 0')
    mqtt.send('log', 'NA,NA,NA,NA,NA,LearnStarted')

    thisbee = {'id': None, 'pump': None, 'amount': None}
    while True:
        frame = cam.grab()
        markers.detect(frame)
        cv2.imshow('f', frame)
        cv2.waitKey(1)
        if markers.being_seen and markers.IDs is not None and not markers.beenRecognized:
            markers.beenRecognized = True
            ID = markers.IDs[0][0]
            seenmarkers.append(ID)
            mqtt.send('debug', 'Seen a  marker - ' + str(ID))

            if not feeder.full:
                if time.time()-feeder.when_emptied > 60:
                    thisbee['id'] = ID
                    thisbee['pump'] = 0
                    thisbee['amount'] = 50000
                    thisbee['quality'] = 'null'
                    thisbee['scent'] = 'null'

                    print(thisbee['amount'])
                    feeder.do_fill(thisbee['pump'], amount=thisbee['amount'])
                    mqtt.send('debug', 'giving '+str(thisbee['id'])+' sugar from pump '+str(thisbee['pump']) +
                              ' of quality '+str(thisbee['quality'])+'and scent '+str(thisbee['scent']) +
                              ' for '+str(thisbee['amount']/1000)+'ul')
                    mqtt.send('log', str(thisbee['id'])+','+str(thisbee['pump']) +
                              ','+str(thisbee['quality'])+','+str(thisbee['scent']) +
                              ','+str(thisbee['amount'])+',filling')
                else:
                    mqtt.send('debug', 'i have seen '+str(ID)+' but the retention time has not elapsed')
                    mqtt.send('log', str(ID)+',NA,NA,NA,NA,retention')
            elif feeder.full:
                mqtt.send('debug', 'the feeder is full already')

        elif not markers.being_seen:
            if feeder.full:
                mqtt.send('debug', 'no bee, emptying the feeder')
                feeder.do_flush(100000)
        if mqtt.got_prime_message:
            feeder.do_prime()
            mqtt.got_prime_message = False

        if mqtt.got_kill_message:
            mqtt.send('debug', 'I got turned off :( Goodnight!')
            mqtt.send('debug', 'in the end I have seen today: '+str(seenmarkers))
            mqtt.send('log', 'NA,NA,NA,NA,NA,Quit')
            led.off()
            break
