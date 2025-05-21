import time
import socket
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq
from zmq.devices import monitored_queue

from zhelpers import zpipe

class room():
    def __init__(self, sala_id):
        self.sala_id = sala_id
        self.listas_ip = []


    def subscriber_thread(self):
        ctx = zmq.Context.instance()

        # Subscribe to "A" and "B"
        subscriber = ctx.socket(zmq.SUB)
        subscriber.connect("tcp://localhost:6001")
        subscriber.setsockopt(zmq.SUBSCRIBE, b"") # mudar esse b"", pois queremos que ai esteja a sala! self.sala

        count = 0
        while True:
            try:
                msg = subscriber.recv_multipart()
                    
                # if tamanho da lista de sockets diferente, faz a conexao nessa porra
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
        publisher.bin("tcp://localhost:6000")

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
            
    def broadcast_presenca(self, port=6002) -> None:
        '''
        Sempre que você estiver entrando em uma sala, um broadcast será feito para todos dispositivos na rede.
        
        Manda duas coisas:
            * DISCOVER_ROOM: string definida para quem estiver em uma sala entender que tem um dispositivo querendo entrar
            * sala_id: identificador de sala
            
        Caso um peer estiver na mesma sala que a requisição foi feita, então haverá um handshake para eles se conectarem.
        
        A função listener_to_peer() recebe as requisições de broadcast_presenca()
        
        A porta para envio de broadcast é 6002 por default
        '''
        msg = b"DISCOVER_ROOM" + b"|" + bytes(self.sala_id)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        s.sendto(msg, ("<broadcast>", port))
        
    def listener_to_peer(self, port=6002) -> None:
        '''
        Escuta na porta 6002 por default sempre que uma requisição para entrar em sala acontece.
        
        Caso sala_id seja igual a nossa, faremos o handshake em outra função...
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        
        while True:
            msg, addr = s.recvfrom(1024)
            msg = str(msg.split(b"|"))
            
            if msg[0] == "DISCOVER_ROOM" and int(msg[1]) == self.sala_id:
                self.listas_ip.append(addr)               
        
    
    def listener_thread (self, pipe):
    
        # Print everything that arrives on pipe
        while True:
            try:
                print (pipe.recv_multipart())
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted