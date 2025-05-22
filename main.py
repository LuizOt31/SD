from sala import room
import time

from random import randint
from threading import Thread

import zmq
from zmq.devices import monitored_queue

from zhelpers import zpipe

def sala(sala_id: int):
    ctx = zmq.Context.instance()

    minha_sala = room(sala_id)

    p_thread = Thread(target=minha_sala.publisher_thread)
    s_thread = Thread(target=minha_sala.subscriber_thread)
    b_thread = Thread(target=minha_sala.broadcast_presenca)
    l_thread = Thread(target=minha_sala.listener_to_peer)

    p_thread.start()
    s_thread.start()
    b_thread.start()
    l_thread.start()
        
    pipe = zpipe(ctx)

    l_pipe = Thread(target=minha_sala.listener_thread, args=(pipe[1],))
    l_pipe.start()
    
    try:
        while True:
            minha_sala.fila.put(input())
            
    except KeyboardInterrupt:
        print("Interrupted")


def main():
    '''
    Função principal que roda nosso "Skype"

    Para entrar em uma sala é preciso digitar um número. Todas as pessoas que digitarem esse número entrarão
    na mesma chamada que você.

    As salas podem ser de texto, voz e video. Será definido na hora que criar a sala. (nao implementado, só futuramente...)
    '''

    print("Seja bem-vindo, digite o número da porta da sala que deseja se conectar")
    num_sala = int(input())

    try:
        sala(num_sala)
    except KeyboardInterrupt:
        print("Saindo...")

if __name__ == "__main__":
    main()
