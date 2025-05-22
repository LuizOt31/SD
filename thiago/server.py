import zmq

context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind("tcp://*:5555")

salas = {}  
clientes_salas = {}  
clientes_nomes = {}  

print("Servidor rodando na porta 5555...")

while True:
    client_id, _, msg = socket.recv_multipart()
    dados = msg.decode().split("||")

    if dados[0] == "ENTRAR":
        sala = dados[1]
        nome = dados[2]

        print(f"{nome} ({client_id.hex()}) entrou na sala {sala}")
        clientes_salas[client_id] = sala
        clientes_nomes[client_id] = nome
        salas.setdefault(sala, []).append(client_id)

        continue

    elif dados[0] == "MSG":
        sala = clientes_salas.get(client_id)
        texto = dados[1]
        nome = clientes_nomes.get(client_id, client_id.hex())

        print(f"[{sala}] {nome}: {texto}")

        for cliente in salas.get(sala, []):
            socket.send_multipart([cliente, b"", f"[@{nome}] {texto}".encode()])
