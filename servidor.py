from socket import *
s = socket(AF_INET, SOCK_STREAM)

s.bind(('127.0.0.1', 8080))
s.listen()
(conn, addr) = s.accept()
while True:
    data = conn.recv(1024)
    if not data: 
        break
    conn.send(data + b"*")

conn.close()