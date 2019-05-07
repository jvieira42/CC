class StatusTable:
	
	def __init__(self):
		self.dictionary = []

	
	def entry(self,type,file_name,ip_orig,port_orig,n_packets):

		dict = {"Type" : type,
				"File" : file_name,
				"IP Origem" : ip_orig,
				"Porta Origem" : port_orig,
				"Número de pacotes" : n_packets,
				"Pacotes recebidos" : 0,				
				"Pacotes perdidos": 0}


		return dict



	def update(self,entry):

		for dict in self.dictionary:
			if dict["Type"] == entry["Type"] and dict["File"] == entry["File"]:
				self.dictionary.remove(dict)

		self.dictionary.append(entry)

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

	def pacoteRecebido(self):
		self.dictionary[-1]["Pacotes recebidos"] += 1
	def pacotePerdido(self):
		self.dictionary[-1]["Pacotes perdidos"] += 1