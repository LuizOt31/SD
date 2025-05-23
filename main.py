from sala_chat import sala_chat
from sala_video import sala_video
from threading import Thread
import cv2
import zmq
import threading

def sala_chat_(minha_sala: sala_chat) -> None:
    try:
        while True:
            minha_sala.fila.put(input(">>>"))     
    except KeyboardInterrupt:
        print("Interrupted")
        return
        
def sala_video_(minha_sala: sala_video) -> None:
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erro na captura de frame")
                break
                
            cv2.imshow("Minha Webcam", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            minha_sala.fila.put(frame)
            
            with minha_sala.fila_lock:
                for ip_peer in minha_sala.fila_peers:
                    if not minha_sala.fila_peers[ip_peer].empty():
                        cv2.imshow(f"{ip_peer}", minha_sala.fila_peers[ip_peer].get())
                
    except KeyboardInterrupt:
        print("Interrupted")
        cap.release()
        cv2.destroyAllWindows()
        return
    

def sala(sala_id: int, tipo_sala: int) -> None:
    '''
    Criação da sala por aqui.
    
    Inicializa as threads da sala e chama a função da sala respectiva para tipo_sala
    '''
    if tipo_sala == 1:
        minha_sala = sala_chat(sala_id)
    elif tipo_sala == 2:
        minha_sala = sala_video(sala_id)

    p_thread = Thread(target=minha_sala.publisher_thread)
    s_thread = Thread(target=minha_sala.subscriber_thread)
    b_thread = Thread(target=minha_sala.broadcast_presenca)
    l_thread = Thread(target=minha_sala.listener_to_peer)

    p_thread.start()
    s_thread.start()
    b_thread.start()
    l_thread.start() 
    
    if tipo_sala == 1:
        sala_chat_(minha_sala)
    elif tipo_sala == 2:
        sala_video_(minha_sala)      

def main():
    '''
    Função principal que roda nosso "Skype"

    Para entrar em uma sala é preciso digitar um número. Todas as pessoas que digitarem esse número entrarão
    na mesma chamada que você.

    As salas podem ser de texto, voz e video. Será definido na hora que criar a sala. (nao implementado, só futuramente...)
    '''

    print("Seja bem-vindo, digite o número da porta da sala que deseja se conectar")
    num_sala = int(input(">>>"))
    print("Tipo da sala\nDigite 1 para chat, 2 para video")
    tipo_sala = int(input(">>>"))
    try:
        sala(num_sala, tipo_sala)
    except KeyboardInterrupt:
        print("Saindo...")

if __name__ == "__main__":
    main()
