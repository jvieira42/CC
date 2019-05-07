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
		print ("Packet Sent: " + str + "\n")

	def receivePacket(self):
		ready = select.select([self.agentSock],[],[])
		packet = 0
		address = ""
		if ready[0]:
			packet,address = self.agentSock.recvfrom(1500)
			packet = json.loads(packet.decode())
		return packet,address
