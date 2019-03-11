import socket
import select

HOST = "127.0.0.1"
PORT = 12345

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((HOST,PORT))

print("UDP server running")

while True:
	data, address = socket.recvfrom(1024)
	if data:
		print("File name:", data)
		file = data.strip()

	f = open(file_name, 'wb')

	while True:
		ready = select.select([sock], [], [], timeout)
		if ready[0]:
			data, address = socket.recvfrom(1024)
			f.write(data)
		else:
			print ("%s Finish!" % file)
			f.close()
			break



