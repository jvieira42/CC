import socket, json, select 



class AgentUDP:



	def __init__(self, address, port):
		self.agentSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.list_address = address
		self.list_port = port
		self.send_addr = ""
		self.send_port = 0
		self.state = "NOTCONNECTED"
		


	def bind(self):
		self.agentSock.bind((self.list_address,int(self.list_port)))

	def sendPacket(self,packet):
		str = json.dumps(packet.packet)
		
		_,ready,_ = select.select([],[self.agentSock],[])
		if ready[0]:
			self.agentSock.sendto(str.encode("utf-8"), (self.send_addr, self.send_port))
		print ("Pacote enviado" + str)

	def receivePacket(self):
		ready = select.select([self.agentSock],[],[])
		packet = 0
		address = ""
		if ready[0]:
			packet,address = self.agentSock.recvfrom(1500)
			packet = json.loads(packet.decode())


		return packet,address
		



	def put_file(self,file):
		print("Sending %s" % file)
		self.agentSock.sendto(file.encode(),self.serveraddress)
		print ("Waiting for response...")
		
		while True:
			reply, address = self.agentSock.recvfrom(1024)
			reply = int(reply.decode())
			print("Response: ",reply)
			if reply == 1:
				print("Connection accepted!")
				f = open (file,"rb")
				data = f.read(1024)
				break
			else:
				print ("Connection refused!")
				data = None
				break


		while (data):
			if(self.agentSock.sendto(data,address)):
				data = f.read(1024)
				time.sleep(0.02)


	def get_file(self, path):
		end = 1
		reply = 0
		while end:
			data, address = self.agentSock.recvfrom(1024)
			if data:
				print("File name:", data)
				print(address)
				reply = input("Accept file from address:\tYes-1 | No - 0 \n" )
				if reply == "1":
					self.agentSock.sendto(reply.encode(),address)
					file = data.decode()
					f = open(path+file, 'wb')
				else:
					self.agentSock.sendto(reply.encode(),address)
					end = 0

			while int(reply):
				ready = select.select([self.agentSock], [], [], 3)
				if ready[0]:	
					data, address = self.agentSock.recvfrom(1024)
					f.write(data)
				
				else:
					print ("%s Finish!" % file)
					f.close()
					reply = 0
					end = 0
					break
