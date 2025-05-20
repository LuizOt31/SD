import time

from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq
from zmq.devices import monitored_queue

from zhelpers import zpipe

class room:
    def __init__(self):
        pass

    def subscriber_thread():
        ctx = zmq.Context.instance()

        # Subscribe to "A" and "B"
        subscriber = ctx.socket(zmq.SUB)
        subscriber.connect("tcp://localhost:6001")
        subscriber.setsockopt(zmq.SUBSCRIBE, b"") # mudar esse b"", pois queremos que ai esteja a sala! self.sala

        count = 0
        while count < 5:
            try:
                msg = subscriber.recv_multipart()
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted
                else:
                    raise
            count += 1

        print ("Subscriber received %d messages" % count)

    def publisher_thread():
        ctx = zmq.Context.instance()

        publisher = ctx.socket(zmq.PUB)
        publisher.bind("tcp://*:6000")

        while True:
            string = "%s-%05d" % (uppercase[randint(0,10)], randint(0,100000))
            try:
                publisher.send(string.encode('utf-8'))
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted
                else:
                    raise
            time.sleep(0.1)         # Wait for 1/10th second