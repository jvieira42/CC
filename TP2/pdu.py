import struct

class PDU:
     
     def __init__(self,offset,length,csum = 0,sequence,data):
          self.frag_offset = offset
          self.pck_len = length
          self.checksum = csum
          self.data = data
          self.frag_seq = sequence

     def checksum_calc(data,src_ip,dest_ip):
          csum = 0
          
          if type(data) != bytes:
               data = bytes(data.encode('utf-8'))

          data_len = len(data)
          
          if (data_len%2) == 1:
               data_len += 1
               data += struct.pack('!B',0)

          for i in range(0,len(data),2):
               w = (data[i] << 8) + (data[i+1])
               csum += w

          csum = (csum >> 16) + (csum & 0xFFFF)

          return ~csum & 0xFFFF

     def checksum_val(data,src_ip,dest_ip,checksum):
          data_len = len(data)

          if (data_len%2) == 1:
               data_len +=1
               data += struct.pack('!B',0)

          for i in range(0,len(data),2):
               w = (data[i] << 8) + (data[i+1])
               checksum += w
               checksum = (checksum >> 16) + (checksum & 0xFFFF)

               return checksum



def makePacket(data,seq_num,n_frag):
     
     packet = PDU(0,data.length(),0,data,seq_num)
     return packet
     


