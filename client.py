import socket
import os
import datetime
import time
HOST = '192.168.2.50'
PORT = 8485
ip_port=(HOST,PORT)

filename = "ghijkl"

socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket1.connect((HOST, PORT))

socket1.sendto(filename.encode(encoding='utf-8'),ip_port)
source=""
with open('test.txt', 'wb') as file_to_write:
    while True:
        data = socket1.recv(1024)
        if not data:
            break
        file_to_write.write(data)
        time.sleep(1)
        print(data)
        source+=data.decode()
    file_to_write.close()
    print(datetime.datetime.now())
socket1.close()



