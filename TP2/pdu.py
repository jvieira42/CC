class PDU:
     

     def __init__(self,type,sequence,offset,csum,data):
          self.packet = {}
          self.packet["type"] = type
          self.packet["sequence"] = sequence
          self.packet["offset"] = offset
          self.packet["csum"] = csum
          self.packet["data"] = data 
