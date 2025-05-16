from socket import *
s = socket(AF_INET, SOCK_STREAM)
s.connect(('127.0.0.1', 8080))
s.send(b"ola mundo")
data = s.recv(1024)
print(data)
s.close()