
from agenteUDP import AgentUDP
from timer import Timer 
from statusTable import StatusTable
from pdu import PDU
import time, sys, threading, select, struct
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
        print("1-Conectar")
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
                                q.put(makePacket("CN",0,0,"",self.agent.send_addr,self.agent.list_address))
                                break

                else: 
                    reply = reply.split(" ")

                    if reply[0]== "put_file":
                        self.statusTL.acquire()
                        self.statusTable.update(self.statusTable.entry("Upload",reply[1],self.agent.list_address,self.agent.list_port,0))
                        self.statusTL.release()

                    elif reply[0] =="ls":
                        self.statusTL.acquire()
                        self.statusTable.print_table()
                        self.statusTL.release()

                    elif reply[0] == "get":
                        if reply[1] == "ls":
                            q.put(makePacket("ls",0,0,"",self.agent.send_addr,self.agent.list_address))
                    
                    elif reply[0] == "get_file":
                        q.put(makePacket("fgt",0,0,reply[1],self.agent.send_addr,self.agent.list_address))


            self.inputLock.acquire()
            if (self.input and not self.connected):
                reply = input("Deseja aceitar a conexão?(y/n)\n")
                q.put(makePacket(reply,0,0,"",self.agent.send_addr,self.agent.list_address))
                if reply == "y":
                    print("Conectado\n INSTRUÇÕES: put_file file | get_file file | get ls \n")
                    self.connected = True

            self.inputLock.release()



    def sender_window (self,n_packets, packets):
        self.rlock.acquire()
        self.start_w = 0
        next_p = 0
        window = min(4, n_packets - self.start_w)
        self.rlock.release()

        if(packets[n_packets-1].packet["type"] == "ACK"):
            self.agent.sendPacket(packets[0])
        else:   
            while (self.start_w < n_packets):
                self.rlock.acquire()

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
            
            
                packet = makePacket("end",next_p,0,"",self.agent.send_addr,self.agent.list_address)
                self.agent.sendPacket(packet[0])    

    
    
    def send_file(self,file,q):
        try:
            fd = open (file,'rb')
            seq = 1
            packets = []
            packet = makePacket("get",0,1,file,self.agent.send_addr,self.agent.list_address)
            packets.append(packet[0])
            data = fd.read(1024)
            while data:
                if sys.getsizeof(data)<1024:
                    break
                packet = makePacket("get",seq,1,data.decode(),self.agent.send_addr,self.agent.list_address)
                packets.append(packet[0])
                seq += 1

            if data:
                packet = makePacket("get",seq,0,data.decode(),self.agent.send_addr,self.agent.list_address)
                packets.append(packet[0])
            
            fd.close()
            self.statusTL.acquire()
            self.statusTable.update(self.statusTable.entry("Upload",file,self.agent.list_port,self.agent.list_port,len(packets)))
            update = makePacket("TU",0,0,self.statusTable.entry("Download",file,self.agent.list_address,self.agent.list_port,len(packets)),self.agent.send_addr,self.agent.list_address)
            self.statusTL.release()
            q.put(update)
            q.put(packets)
        except IOError:
            print("Can't open file for sending")
            q.put(makePacket("err",0,0,"Server can't open file for sending",self.agent.send_addr,self.agent.list_address))

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
        
        csum = checksum_calc(packet["data"],self.agent.send_addr,self.agent.list_address)

        if packet["type"] == "ACK":
            self.receive_akn(packet)

        elif(packet["sequence"] == expected and csum == packet["csum"]):
        
            if packet["type"] != "end":

                q.put(makePacket("ACK",expected,packet["offset"],"",self.agent.send_addr,self.agent.list_address))
                expected += 1

                if packet["type"] == "CN":    
                    self.inputLock.acquire()
                    self.input = True
                    self.inputLock.release()
                
                elif (packet["type"] == "y"):
                    self.inputLock.acquire()
                    self.connected = True
                    self.inputLock.release()
                    print("Conectado\n INSTRUÇÕES: put_file file | get_file file | get ls\n")

                elif (packet["type"] == "TU"):
                    self.statusTL.acquire()
                    self.statusTable.update(packet["data"])
                    self.statusTL.release()

                
                elif (packet["type"] == "ls"):
                    self.statusTL.acquire()
                    table = self.sendTable("Upload")
                    self.statusTL.release()
                    if table:
                        q.put(table)
                    else:
                        q.put(makePacket("err",0,0,"No Files!",self.agent.send_addr,self.agent.list_address))

                
                elif (packet["type"] == "ST"):
                    print(packet["data"])

                elif(packet["type"] == "fgt"):
                        if self.statusTable.has_file(packet["data"]):
                            Thread(target=self.send_file,args=(packet["data"],q)).start()
                        else:
                            q.put(makePacket("err",0,0,"No file " + packet["data"] +" found!",self.agent.send_addr,self.agent.list_address))

                elif(packet["type"] == "err"):
                        print(packet["data"])              

                elif(packet["type"] == "get"):

                    if (packet["sequence"] == 0):

                        try:
                            file = open(packet["data"],'wb')
                            print ("Receiving file!")
                        
                        except IOError:
                            print ("Can't open file!\n")


                    else:
                        file.write(packet["data"].encode())

                        if(packet["offset"] == 0):
                            file.close()
                    
                    self.statusTL.acquire()
                    self.statusTable.pacoteRecebido()
                    self.statusTL.release()

            else:
                expected = 0

        else:
            q.put(makePacket("ACK",expected-1,packet["offset"],"",self.agent.send_addr,self.agent.list_address))
            
        return expected,file



    def sendTable(self,type):
        table = self.statusTable.get_type(type)
        seq_number = 0
        packets = []
        for entry in table:
            packet = makePacket("ST",seq_number,1,entry,self.agent.send_addr,self.agent.list_address)
            packets.append(packet[0])
            seq_number+=1

        return packets

def checksum_calc(data,src_ip,dest_ip):
     checksum = 0

     b_src = bytes(src_ip.encode('utf-8'))
     b_dest = bytes(dest_ip.encode('utf-8'))
     
     if type(data) == dict: 
         data = data["File"]

     if type(data) != bytes:
          data = bytes(data.encode('utf-8'))

     data_len = len(data)
     src_len = len(b_src)
     dest_len = len(b_dest)

     if (data_len%2) == 1:
          data_len += 1
          data += struct.pack('!B',0)

     for i in range(0,len(data),2):
          w = (data[i] << 8) + (data[i+1])
          checksum += w
     
     if (src_len%2) == 1:
          src_len += 1
          b_src += struct.pack('!B',0)

     for i in range(0,len(b_src),2):
          w = (b_src[i] << 8) + (b_src[i+1])
          checksum += w
     
     if (dest_len%2) == 1:
          dest_len += 1
          b_dest += struct.pack('!B',0)

     for i in range(0,len(b_dest),2):
          w = (b_dest[i] << 8) + (b_dest[i+1])
          checksum += w

     checksum = (checksum >> 16) + (checksum & 0xFFFF)
     
     return checksum


def makePacket(type,seq_number,offset,data,src_ip,dest_ip):
    packet = PDU(type,seq_number,offset,0,data)
    packet.packet["csum"] = checksum_calc(data,src_ip,dest_ip)
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






