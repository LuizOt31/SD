
import time 
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq
from zmq.devices import monitored_queue

from zhelpers import zpipe
 
class room():
    def __init__(self, sala_id):
        self.sala_id = sala_id


    def subscriber_thread(self):
        ctx = zmq.Context.instance()

        # Subscribe to "A" and "B"
        subscriber = ctx.socket(zmq.SUB)
        subscriber.connect("tcp://localhost:6000")
        subscriber.setsockopt(zmq.SUBSCRIBE, b"") # mudar esse b"", pois queremos que ai esteja a sala! self.sala

        count = 0
        while True:
            try:
                msg = subscriber.recv_multipart()
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted
                else:
                    raise
            count += 1

        print ("Subscriber received %d messages" % count)

    def publisher_thread(self):
        ctx = zmq.Context.instance()

        publisher = ctx.socket(zmq.PUB)
        publisher.connect("tcp://localhost:6001")

        while True:
            msg = input()
            try:
                publisher.send(msg.encode('utf-8'))
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted
                else:
                    raise
            time.sleep(0.1)         # Wait for 1/10th second
            
    
    def listener_thread (self, pipe):
    
        # Print everything that arrives on pipe
        while True:
            try:
                print (pipe.recv_multipart())
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted