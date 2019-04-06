
from agenteUDP import AgentUDP
import sys



def main():	
	address = sys.argv[1].split(":")
	agentUDP = AgentUDP(address[0],address[1])
	while True:
		Userinput = input("Command Instruction:\n\t get <file_path>\n\t put <file_path>\n")
		cmd = Userinput.split(" ", 1)
		file = cmd[1]
		if (cmd[0] == "put"):
			agentUDP.put_file(file)
		elif (cmd[0] == 'get'):
			agentUDP.get_file(file)


main()