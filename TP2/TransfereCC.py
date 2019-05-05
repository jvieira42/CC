
from agenteUDP import AgentUDP
from timer import Timer 
from pdu import PDU
import time, sys, threading, select
from queue import Queue
from threading import Thread


class TransfereCC:



    def __init__(self, agenteUDP):
        self.agent = agenteUDP
        self.start_w = 0
        self.send_time = Timer(2)
        self.input = False
        self.connected = False
        self.rlock = threading.RLock()
        self.inputLock = threading.RLock()
        self.cond = threading.Condition()

    

    def sender_window (self,n_packets, packets):
        self.rlock.acquire()
        self.start_w = 0
        self.rlock.release()
        next_p = 0
        window = min(4, n_packets - self.start_w)
        
        while (self.start_w < n_packets):
            self.rlock.acquire()
            while next_p < self.start_w + window:
                self.agent.sendPacket(packets[next_p])
                next_p += 1

            if not self.send_time.running():
                self.send_time.start()

            while self.send_time.running() and not self.send_time.timeout():
                self.rlock.release()
                time.sleep(0.05)
                self.rlock.acquire()

            if self.send_time.timeout():
                self.send_time.stop()
                print("TIMEOUT; RESENDING...")
                next_p = self.start_w

            else:
                window = min(4, n_packets - self.start_w)

            self.rlock.release()
        
        print ("Base: " + str(self.start_w) + "Window: " + str(window) + "NPacks: " + str(n_packets))
        if(packets[n_packets-1] != "akw"):
            packet = makePacket("",next_p,0)
            self.agent.sendPacket(packet[0])    

    
    
    def receive_akn(self,packet):
        self.rlock.acquire()
        if packet["sequence"] >= self.start_w:
            self.start_w += packet["sequence"] + 1
            self.send_time.stop()
        self.rlock.release()






    def receiver_window(self,packet,q,expected,address):

        self.agent.send_addr = address[0]
        self.agent.send_port = int(address[1])
        
        if packet["data"] == "akw" or packet["data"]=="":
            self.receive_akn(packet)

        
        elif(packet["sequence"] == expected):                    
            q.put(makePacket("akw",expected,1))
            expected += 1

            if packet["data"] == "CN":    
                self.inputLock.acquire()
                self.input = True
                self.inputLock.release()
            
            elif (packet["data"] == "y"):
                self.inputLock.acquire()
                self.connected = True
                self.inputLock.release()
                print("Conectado")

                
            else:
                q.put(makePacket("akw",expected-1,1))
            
        return expected



    def listen(self,q):
        self.agent.bind()
        print ("Entrei\n")
        expected = 0
        while True: 
            packet,address = self.agent.receivePacket()
            expected = self.receiver_window(packet,q,expected,address)


            while (packet["offset"] == 1):
                packet,address = self.agent.receivePacket()
                expected = self.receiver_window(packet,q,expected,address)



    def sender(self,q):
        while True:
            while (not q.empty()):
                packets = q.get()
                self.sender_window(len(packets),packets)    


    def client(self,q):
        print("1-Conectar\n")
        while True:


            ready = select.select([sys.stdin],[],[],1)[0]
            if ready:
                reply = sys.stdin.readline().rstrip('\n')
                

                if not self.connected:
                    if reply == "1" :
                        print("IP:PORTA para a conexão:\n")
                        while True:
                            ready = select.select([sys.stdin],[],[],1)[0]
                            if ready:
                                address = sys.stdin.readline().rstrip('\n')
                                addr = address.split(":")
                                self.agent.send_addr = addr[0]
                                self.agent.send_port = int(addr[1])
                                q.put(makePacket("CN",0,1))
                                break

                else:...

            self.inputLock.acquire()
            if (self.input and not self.connected):
                print(str(self.input) + str(self.connected))
                reply = input("Deseja aceitar a conexão?\n")
                q.put(makePacket(reply,0,1))
                if reply == "y":
                    self.connected = True

            self.inputLock.release()



def makePacket(data,seq_number,offset):
    packet = PDU(offset,len(data),seq_number,data,0)
    return [packet]



def main(): 
    address = sys.argv[1].split(":")
    agentUDP = AgentUDP(address[0],address[1])
    transfereCC = TransfereCC(agentUDP)
    q = Queue()
    thread1 = Thread(target=transfereCC.listen,args=[q])
    thread2 = Thread(target=transfereCC.sender,args=[q])
    thread1.start()
    thread2.start()
    transfereCC.client(q)

main()






