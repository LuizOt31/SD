from teste2 import room
from random import randint
from threading import Thread
import time
import zmq
from zmq.devices import monitored_queue

from zhelpers import zpipe

def entrar_sala():
    print("Em construção...")
    ...


def criar_sala(tipo: int):
    ctx = zmq.Context.instance()
    sala_id = randint(1000, 10000)

    if tipo == 1:
        sala = room(sala_id)

        p_thread = Thread(target=sala.publisher_thread)
        s_thread = Thread(target=sala.subscriber_thread)
        p_thread.start()
        s_thread.start()
            
        pipe = zpipe(ctx)
            
        subscriber = ctx.socket(zmq.XSUB)
        subscriber.connect("tcp://localhost:6001")
    
        publisher = ctx.socket(zmq.XPUB)
        publisher.bind("tcp://*:6000")
    
        l_thread = Thread(target=sala.listener_thread, args=(pipe[1],))
        l_thread.start()
    
        try:
            monitored_queue(subscriber, publisher, pipe[0], b'pub', b'sub')
        except KeyboardInterrupt:
            print ("Interrupted")

    else: # Corrijir futuramente
        return

def main():
    '''
    Função principal que roda nosso "Skype"

    Há duas opções:
        * Entrar em uma sala
        * Criar uma sala, que consequentemente, entra nela também

    As salas podem ser de texto, voz e video. Será definido na hora que criar a sala.
    '''

    print("Digite o numero que deseja fazer")
    print("1. Entrar em uma sala\n2. Criar uma sala")
    aux = int(input())

    if aux == 1:
        entrar_sala()
    elif aux == 2:
        print("Sua sala será em que formato? (digite o número por favor)")
        print("1. Texto\n2. Audio\n3. Video")
        tipo_sala = int(input())

        criar_sala(tipo_sala)
    else:
        print("Vai toma no CU, faz essa porra direito")
        return


if __name__ == "__main__":
    main()
