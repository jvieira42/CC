
import sys

import time

import socket


UDP_IP = "127.0.0.1"
UDP_PORT = 12345

file = sys.argv[1]

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

clientSock.sendto(bytes(file,"UTF-8"), (UDP_IP, UDP_PORT))

print("Sending %s" % file)

f = open (file,"rb")
data = f.read(1024)

while (data):
	if(clientSock.sendto(data,(UDP_IP, UDP_PORT))):
		data = f.read(1024)
		time.sleep(0.02)
