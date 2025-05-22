import zmq

ctx = zmq.Context()

broker_msg_sub = ctx.socket(zmq.XSUB)
broker_msg_sub.bind("tcp://127.0.0.1:7000")
broker_msg_pub = ctx.socket(zmq.XPUB)
broker_msg_pub.bind("tcp://127.0.0.1:7001")

# toda mensagem que é recebida é enviada
zmq.proxy(broker_msg_sub, broker_msg_pub)

# criar sockets pub/sub para oso canais de audio e video