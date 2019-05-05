import struct

class PDU:
     
     def __init__(self,offset,length,sequence,data,csum = 0):
          self.packet = {}
          
          self.packet["offset"] = offset
          self.packet["length"] = length
          self.packet["sequence"] = sequence
          self.packet["csum"] = csum
          self.packet["data"] = data 

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




     


