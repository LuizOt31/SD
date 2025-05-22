import zmq
import threading
import time

def receber_msg(sub):
    while True:
        try:
            msg = sub.recv_string()
            # melhorar print, tirar o tópico aparecendo no início da mensagem
            # deixar só o conteúdo/nome de quem enviou
            print(msg)
        except Exception:
            break

"""
cliente se inscreve no broker com um tópico específico
e envia mensagens usando esse tópico
o broker repassa as mensagens recebidas para todos os clientes
inscritos naquele tópico específico
"""

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://127.0.0.1:7000")
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:7001")

nome = input("Seu nome: ")
topico = input("Digite o nome de um grupo ou usuário para conversar: ")
# melhorar entrada de dados, menu etc
# possivel melhoria: padronizar nomes dos tópicos
# exemplo: GRUPO/{nome} ou PRIV/{nome} de acordo com a escolha
sub.setsockopt_string(zmq.SUBSCRIBE, topico) # cliente só recebe mensagens que começam com esse tópico

threading.Thread(target=receber_msg, args=(sub,), daemon=True).start()
time.sleep(1) # delay pra conexão

while True:
    txt = input("> ")
    if not txt:
        continue
    # msg começa com o tópico para o broker encaminhar corretamente
    # adicionar nome de quem enviou pra melhorar outrput
    pub.send_string(topico + " " + txt)