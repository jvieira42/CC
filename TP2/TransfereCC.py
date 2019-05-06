
from agenteUDP import AgentUDP
from timer import Timer 
from statusTable import StatusTable
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
        self.statusTL = threading.RLock()
        self.cond = threading.Condition()
        self.statusTable = StatusTable()



    def listen(self,q):
        self.agent.bind()
        print ("Entrei\n")
        file = 0
        expected = 0
        while True: 
            packet,address = self.agent.receivePacket()
            expected,file = self.receiver_window(packet,q,expected,address,file)


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
                                q.put(makePacket("CN",0,0,""))
                                break

                else: 
                    reply = reply.split(" ")

                    if reply[0]== "put_file":
                        self.statusTL.acquire()
                        self.statusTable.update("Upload",reply[1],self.agent.list_address,self.agent.list_port)
                        self.statusTL.release()

                    elif reply[0] =="ls":
                        self.statusTL.acquire()
                        self.statusTable.print_table()
                        self.statusTL.release()

                    elif reply[0] == "get":
                        if reply[1] == "ls":
                            q.put(makePacket("ls",0,0,""))
                    
                    elif reply[0] == "get_file":
                        q.put(makePacket("fgt",0,0,reply[1]))


            self.inputLock.acquire()
            if (self.input and not self.connected):
                print(str(self.input) + str(self.connected))
                reply = input("Deseja aceitar a conexão?\n")
                q.put(makePacket(reply,0,0,""))
                if reply == "y":
                    print("Conectado\n INSTUÇÕES: put_file file | \n")
                    self.connected = True

            self.inputLock.release()



    def sender_window (self,n_packets, packets):
        self.rlock.acquire()
        self.start_w = 0
        next_p = 0
        window = min(4, n_packets - self.start_w)
        self.rlock.release()

        
        while (self.start_w < n_packets):
            self.rlock.acquire()
            print ("Base: " + str(self.start_w) + "Window: " + str(window) + "NPacks: " + str(n_packets) + "Next_Packet: " + str(n_packets))

            while next_p < self.start_w + window:
                self.agent.sendPacket(packets[next_p])
                next_p += 1

            if not self.send_time.running():
                self.send_time.start()

            while self.send_time.running() and not self.send_time.timeout():
                self.rlock.release()
                time.sleep(0.5)
                self.rlock.acquire()

            if self.send_time.timeout():
                self.send_time.stop()
                print("TIMEOUT; RESENDING...")
                next_p = self.start_w

            else:
                window = min(4, n_packets - self.start_w)

            self.rlock.release()
        
        if(packets[n_packets-1].packet["type"] != "akw"):
            packet = makePacket("end",next_p,0,"")
            self.agent.sendPacket(packet[0])    

    
    
    def send_file(self,file,q):
        print ("OPENED FILE")
        try:
            fd = open (file,'rb')
            seq = 1
            packets = []
            packet = makePacket("get",0,1,file)
            packets.append(packet[0])
            data = fd.read(1024)
            while data:
                if sys.getsizeof(data)<1024:
                    break
                packet = makePacket("get",seq,1,data.decode('utf-8'))
                packets.append(packet[0])
                seq += 1

            if data:
                packet = makePacket("get",seq,2,data.decode('utf-8'))
                packets.append(packet[0])
            
            q.put(packets)
            fd.close()
        except IOError:
            print("Can't open file for sending")
            q.put(makePacket("err",0,0,"Server can't open file for sending"))




    def receive_akn(self,packet):
        self.rlock.acquire()
        if packet["sequence"] >= self.start_w:
            self.start_w += 1
            self.send_time.stop()
        self.rlock.release()
   




    def receiver_window(self,packet,q,expected,address,file):
        table = []
        self.agent.send_addr = address[0]
        self.agent.send_port = int(address[1])
        print (packet)
        print ("EXPECTED: " + str(expected))
        
        if packet["type"] == "akw" or packet["type"] == "end":
        	self.receive_akn(packet)
        	if (packet["type"] == "akw" and packet["offset"] != 0 and packet["sequence"] == expected):
        		print("ENTREI Expexted ++ ")
        		expected += 1
        	
        	if packet["offset"] == 0:
        		print("EXPECTED == 0")
        		expected = 0


        
        elif(packet["sequence"] == expected and packet["type"] != "get"):                    
            q.put(makePacket("akw",expected,packet["offset"],""))
            expected += 1
            print(expected)

            if packet["type"] == "CN":    
                self.inputLock.acquire()
                self.input = True
                self.inputLock.release()
            
            elif (packet["type"] == "y"):
                self.inputLock.acquire()
                self.connected = True
                self.inputLock.release()
                print("Conectado\n INSTRUÇÕES: put_file file | \n")

            elif (packet["type"] == "ls"):
                self.statusTL.acquire()
                table = self.sendTable("Upload")
                self.statusTL.release()
                if table:
                    q.put(table)
                else:
                    q.put(makePacket("err",0,0,"No Files!"))

            elif (packet["type"] == "ST"):
                print(packet["data"])


            elif(packet["type"] == "get"):

                if (packet["sequence"] == 0):
                    self.statusTL.acquire()
                    try:
                        file = open(packet["data"],'wb')
                        self.statusTable.update("Download",packet["data"],self.agent.send_addr,self.agent.send_port)
                        print ("Receiving file!")
                    
                    except IOError:
                        print ("Can't open file!\n")

                    self.statusTL.release()

                else:
                    file.write(packet["data"].encode())
                    if(packet["offset"] == 2):
                        file.close()
            	

            elif(packet["type"] == "fgt"):
                    if self.statusTable.has_file(packet["data"]):
                        Thread(target=self.send_file,args=(packet["data"],q)).start()


            elif(packet["type"] == "err"):
                    print(packet["data"])




                                
        else:
        	q.put(makePacket("akw",expected-1,packet["offset"],""))
        	print ("ERRO!!!!!")
            
        
        return expected,file



    def sendTable(self,type):
        table = self.statusTable.get_type(type)
        seq_number = 0
        packets = []
        for entry in table:
            packet = makePacket("ST",seq_number,1,entry)
            packets.append(packet[0])
            seq_number+=1

        return packets



def makePacket(type,seq_number,offset,data):

    packet = PDU(type,seq_number,offset,0,data)
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






