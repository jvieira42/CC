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
		table = []
		for dict in self.dictionary:
			if dict["Type"] == type: 
				table.append(dict)
		return table

	def has_file(self,file):
		for dict in self.dictionary:
			if dict ["Type"] == "Upload" and dict["File"] == file:
				return True

		return False