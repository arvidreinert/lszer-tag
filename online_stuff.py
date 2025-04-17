import pickle
import socket
PORT = 9000
class server_manager():
    def __init__(self,ip):
        self.server_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_s.connect((ip, PORT))
        answer = self.send_and_listen("login")
        if answer.split(",")[0] == "logged in succesfull":
            self.s_peers = int(answer.split(",")[1])
        else:
            print("Fatal error!")

    def send(self,msg):
        msg = pickle.dumps(msg)
        self.server_s.sendall(msg)

    def send_and_listen(self,msg):
        self.send(msg)
        received_data = pickle.loads(self.server_s.recv(4096))
        return received_data
