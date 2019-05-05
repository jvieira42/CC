class StatusTable:
	
	def __init__(self):
		self.dictionary = []

	def update(self,type,file_name,ip_orig,port_orig):

		dict = {"Type" : type,
				"File" : file_name,
				"IP Origem" : ip_orig,
				"Porta Origem" : port_orig}

		self.dictionary.append(dict)

	def print_table(self):
		print(self.dictionary) 


	def get_type(self,type):
		for dict in self.dictionary:
			if dict["Type"] == type: 
				print(dict["Type"])



StatusTable = StatusTable()
StatusTable.update("PUT","","","")
StatusTable.get_type("PUT")