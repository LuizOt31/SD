from queue import Queue
import numpy as np
import time
import socket
import subprocess
import cv2
import zmq
import pickle
import imutils
import struct
import io

class sala_video():
    def __init__(self, sala_id: int, tipo_sala = 1):
        '''
        sala_id = identificador da sala
        tipo_sala = 1. chat, 2. video
        '''
        self.sala_id = sala_id
        self.tipo_sala = tipo_sala
        self.lista_ip = []
        self.sockets_connect = {}
        self.fila = Queue()
        self.running = True
        self.meu_ip = subprocess.run("hostname -I | awk '{print $1}'", shell=True, capture_output=True, text=True).stdout.strip()

    def subscriber_thread(self) -> None:
        '''
        O subscriber é quem se conecta com outros peers. Cada ip que listener_to_peer() achar, essa função aqui
        irá criar um socket e se conectar a esse ip na porta 6000 para escutar o que ele está mandando.
        
        Isso é bom, pois dessa maneira é mais fácil de controlar as mensagens de cada peer conectado
        '''
        ctx = zmq.Context.instance()
        socket_to_ip = {}

        data = b""
        payload_size = struct.calcsize(">L")
        print("payload_size: {}".format(payload_size))
        
        poller = zmq.Poller()
        
        # continua enquanto a sala estiver viva
        while self.running:
            for ip in self.lista_ip:
                if ip not in self.sockets_connect:
                    try:
                        # caso tenha algum ip não mapeado para socket ainda, o código abaixo mapeia
                        # aux_socket é uma variavel auxiliar
                        aux_socket = ctx.socket(zmq.SUB)
                        aux_socket.connect(f"tcp://{ip}:52222")
                        aux_socket.setsockopt(zmq.SUBSCRIBE, '')
                        
                        self.sockets_connect[ip] = aux_socket
                        socket_to_ip[aux_socket] = ip
                        
                        # Todos os sockets são registrados no poller, pois ele trata manejamento de vários sockets ao mesmo tempo
                        poller.register(self.sockets_connect[ip], zmq.POLLIN)
                        
                        print(f"[SYSTEM] Conectado ao ip: {ip}")
                    except zmq.ZMQError:
                        continue
            
            # poller.poll() espera 0.1s. Se nenhum socket obteve resposta dos outros peers, retorna {} (dicionario vazio)
            # ou seja, só retorna os sockets que tiveram alguma resposta.
            socks = dict(poller.poll(100))
            # Recebendo Video
            for sock in socks:
                if sock in socket_to_ip: # Será q precisa?
                    topic, frame_data = sock.recv_multipart()

                    frame = cv2.imdecode(
                        np.frombuffer(frame_data, dtype = np.uint8),
                        cv2.IMREAD_COLOR
                    )

                    if frame is not None:
                        cv2.imshow(f"{socket_to_ip[sock]}", frame)
                        cv2.waitKey(1)        
                            
    def publisher_thread(self) -> None:
        '''
        Publisher é quem publica as mensagens enviadas por esse processo. Ele apenas publica, é função 
        do subscriber dos outros peers se ligar e ouvir as mensagens.

        a função tem um loop infinito e fica tentando pegar o elemento da FIFO para mandar pro socket
        '''
        ctx = zmq.Context.instance()

        publisher = ctx.socket(zmq.PUB)
        publisher.bind("tcp://*:52222")

        img_counter = 0
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        while True:
            if not self.fila.empty():

                # Pega o primeiro elemento da FIFO para enviar
                msg = self.fila.get()
                try:
                    frame = imutils.resize(msg, width=320)
                    frame = cv2.flip(frame, 180)

                    # Codifica o frame para JPEG
                    result, encoded_image = cv2.imencode('.jpg', frame, encode_param)

                    # data = pickle.dumps(image, 0)
                    # size = len(data)

                    if img_counter % 10 == 0:
                        publisher.send_multipart([
                            str(self.sala_id).encode('utf-8'),  # Tópico/filtro
                            encoded_image.tobytes()  
                        ])

                    img_counter += 1

                except zmq.ZMQError as e:
                    if e.errno == zmq.ETERM:
                        break           # Interrupted
                    else:
                        raise
                time.sleep(0.1)         # Não força tanto a CPU
            
    def broadcast_presenca(self, port=52223) -> None:
        '''
        Sempre que você estiver entrando em uma sala, um broadcast será feito para todos dispositivos na rede.
        
        Manda duas coisas:
            * DISCOVER_ROOM: string definida para quem estiver em uma sala entender que tem um dispositivo querendo entrar
            * sala_id: identificador de sala
            
        Caso um peer estiver na mesma sala que a requisição foi feita, então haverá um handshake para eles se conectarem.
        
        A função listener_to_peer() recebe as requisições de broadcast_presenca()
        
        A porta para envio de broadcast é 6002 por default
        '''
        msg = b"DISCOVER_ROOM" + b"|" + str(self.sala_id).encode('utf-8') + b"|" + str(self.tipo_sala).encode('utf-8')

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        count = 0
        while True:
            if count == 0:
                print("Mandando em broadcast pela primeira vez, vamo achar alguem!")
                count += 1
            
            s.sendto(msg, ("<broadcast>", port))

            time.sleep(10)
        
        return
        
    def listener_to_peer(self, port=52223) -> None:
        '''
        Função que espera requisições para entrar na mesma sala, recebe as duas coisas citadas na função broadcast_presenca()

        Se identificar que é um "DISCOVER_ROOM" e o identificador da sala sala_id for o mesmo, a função guarda o endereço para se
        conectar ao outro dispositivo. Além disso, também manda uma mensagem para o dispositivo que o chamou, dizendo que irá se conectar
        e é para ele se conectar também, por isso o elif ali embaixo com "ROOM_DISCOVERED"
        '''

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # cpa o problema é aqui
        s.bind(('', port))
        
        try:
            while True:
                msg, addr_outroPeer = s.recvfrom(1024)
                msg_parts = msg.decode().split("|")

                if addr_outroPeer[0] != '127.0.1.1' and addr_outroPeer[0] != '127.0.0.1' and addr_outroPeer[0] != self.meu_ip:

                    if msg_parts[0] == "DISCOVER_ROOM" and int(msg_parts[1]) == self.sala_id and int(msg_parts[2]) == self.tipo_sala:
                        if addr_outroPeer[0] not in self.lista_ip:
                            self.lista_ip.append(addr_outroPeer[0])
                            print(f"Alguém esta chamando, seu ip é: {addr_outroPeer[0]}")
        
        except KeyboardInterrupt:
            pass
        
    def listener_thread (self, pipe):
    
        # Print everything that arrives on pipe
        while True:
            try:
                print (pipe.recv_multipart())
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    break           # Interrupted
