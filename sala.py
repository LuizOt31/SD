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
        self.sockets_connect = {}


    def subscriber_thread(self):
        ctx = zmq.Context.instance()

        subscriber = ctx.socket(zmq.SUB)
        subscriber.connect("tcp://localhost:6001")
        subscriber.setsockopt(zmq.SUBSCRIBE, b"") # mudar esse b"", pois queremos que ai esteja a sala! self.sala

        while True:
            try:
                # if tamanho da lista de sockets diferente, faz a conexao nessa porra
                ip_nova_conexao = self.listas_ip[-1]

                if ip_nova_conexao is not None and ip_nova_conexao not in self.sockets_connect:
                    self.sockets_connect[ip_nova_conexao] = subscriber.connect(f"tcp://{ip_nova_conexao}:6001")

                msg = subscriber.recv_multipart()

                # Acho que aqui vai printar as mensagens recebidas
                print(msg)

            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted
                else:
                    raise

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
        Função que espera requisições para entrar na mesma sala, recebe as duas coisas citadas na função broadcast_presenca()

        Se identificar que é um "DISCOVER_ROOM" e o identificador da sala sala_id for o mesmo, a função guarda o endereço para se
        conectar ao outro dispositivo. Além disso, também manda uma mensagem para o dispositivo que o chamou, dizendo que irá se conectar
        e é para ele se conectar também, por isso o elif ali embaixo com "ROOM_DISCOVERED"
        '''

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        
        while True:
            msg, addr = s.recvfrom(1024)
            msg = str(msg.split(b"|"))
            
            if msg[0] == "DISCOVER_ROOM" and int(msg[1]) == self.sala_id:
                self.listas_ip.append(addr[0])

                # Após reconhecer que é a mesma sala, envia uma mensagem dizendo que irá se conectar, para que os dois se conectem
                msg = b"ROOM_DISCOVERED" + b"|" + bytes(self.sala_id)

                udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                udp_socket.sendto(msg, addr)

                udp_socket.close()   

            # Checagem para ver se consegui descobrir outras pessoas na mesma sala que a minha
            elif msg[0] == "ROOM_DISCOVERED" and int(msg[1]) == self.sala_id:
                # addr[0] para passar apenas o IP, não precisamos da porta 6002, já que nos conectamos pela 6001
                self.listas_ip.append(addr[0])
        
    
    def listener_thread (self, pipe):
    
        # Print everything that arrives on pipe
        while True:
            try:
                print (pipe.recv_multipart())
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted