# 客户端
import socket

client = socket.socket()
client.connect(("127.0.0.1", 8888))

while True:
    message = input("kaka")
    if message == str(0):
        break
    else:
        client.send(message.encode("utf8"))

client.close()