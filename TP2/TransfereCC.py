
from agenteUDP import AgentUDP
import sys
import time
from queue import Queue
from threading import Thread



class TransfereCC:



    def __init__(self, agenteUDP):
        self.agent = agenteUDP
        self.start_w = 0
        self.send_time = Timer(0.5)
        self.rlock = RLock()
        self.cond = Condition()

    

    def sender_window (self,n_packets, packets):
        self.rlock.acquire()
            self.start_w = 0
        next_p = 0
        window = min(4, n_packets - self.start_w)
        while (self.start_w < n_packets):
            self.rlock.acquire()

            while next_p < self.start_w + window:
                self.agent.sendPacket(packets[next_p])
                next_p += 1

            if not self.send_time.running():
                send_time.start()

            while send_time.running() and not send_time.timeout():
                self.rlock.release()
                time.sleep(0.05)
                self.rlock.acquire()

            if send_time.timeout():
                send_time.stop()
                next_p = base

            else:
                window = min(4, n_packets - self.start_w)

            self.rlock.release()
                

    
    
    def receive_akn(packet):
        if packet >= base:
            self.rlock.acquire()
            base += packet+1
            self.send_time.stop()
            self.rlock.release()






    def receiver_window(self,packets,expected):
        expected = 0
        for packet in packets:    

            if (packet.seq_num == expected):
                
                q.put (expected)
                expected += 1

            else:
                q.put(expected-1)

            return expected





    def listen(self,q):
        self.agent.bind()
        print ("Entrei\n")
        while True: 
            packet,address = self.agent.receivePacket()
            packet = packet.decode()
            print(packet)
            #checksum
            q.put("akw")
            if packet == "CN":    
                self.agent.send_addr = address[0]
                self.agent.send_port = address[1]
                reply = input("Aceitar conexão?")
                #prepare packet
                q.put(reply)


            elif (packet == "y"):
                self.agent.send_addr = address[0]
                self.agent.send_port = int(address[1])
                #prepare packet
                q.put("y") 

            elif (packet == "akw"):
                receive_akn(packet)





    def sender(self,q):
        while True:
            while (not q.empty()):
                i = 0
                while(i<q.qsize())
                    packets[i++] = q.get()

                self.sender_window(q.qsize(),packets)    


    def client(self,q):
        while True:
            reply = input("1-Connectar\n")
            if reply == "1":
                address = input("IP:PORTA para connectar:\n")
                addr = address.split(":")
                self.agent.send_addr = addr[0]
                self.agent.send_port = int(addr[1])
                
                q.put("CN")
                with self.agent.cond:
                    cv.wait()
                





    def connect(self,ip_addr,port):
        changeState("TC")
        self.send_addr = ip_addr
        self.send_port = port
        i=0
        while (self.state == "TC" and i<10):
            self.agentSock.sendto("CR".encode(),self.send_addr,self.port)
            time.sleep(1)
            print ("Retrying...")
            i = i+1

        if (self.state == "TC"):
            changeState("DC")
            print ("No response from server")

        elif (self.state == "CN"):
            print("Connected!")

            





def main(): 
    address = sys.argv[1].split(":")
    agentUDP = AgentUDP(address[0],address[1])
    tipo = "S"
    transfereCC = TransfereCC(agentUDP,tipo)
    q = Queue()
    thread1 = Thread(target=transfereCC.listen,args=[q])
    thread2 = Thread(target=transfereCC.sender,args=[q])
    thread1.start()
    thread2.start()
    transfereCC.client(q)

main()






