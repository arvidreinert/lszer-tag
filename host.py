#http127.0.0.1 port 9000
import pickle
import socket
import select
import pygame
hn = socket.gethostname()
ai = socket.getaddrinfo(hn,None)
for a in ai:
    if a[0] == socket.AF_INET:
        ip = a[4][0]
        break
clock = pygame.time.Clock()
PORT = 9000 
players_connected = {}
last_action_to = ()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", PORT))
print(f"server: {hn}.local ({ip})")
#to who, what
actions_receveid = "False"
message_count = 0
message_history = []
while True:
    ready,_,_, = select.select([s],[],[],1)
    if ready:
        data,addr = s.recvfrom(4096)
        data = pickle.loads(data)
        if data == "break":
            print("shutting down server")
            break

        if data == "login":
            players_connected[addr[1]] = data
            print(players_connected)
            s.sendto(pickle.dumps(f"logged in succesfull,{len(list(players_connected))}"), addr)
        if data == "req peer online":
            l = len(list(players_connected))
            s.sendto(pickle.dumps(str(l)), addr)

        if "actio;" in data:
            print("received from:", addr)
            #output: ['actio', "['create:card0,arvid_charzard_deck0.png,arvid_charzard_deck0.png0']"]
            actions_receveid = data.split(";")[1]
            last_action_to = addr
            print(actions_receveid)

        if data == "req:actio":
            if actions_receveid == "False":
                s.sendto(pickle.dumps("False"), addr)
            else:
                if last_action_to[1] == addr[1]:
                    s.sendto(pickle.dumps("False"), addr)
                else:
                    print("sent to:",addr,"count:",message_count)
                    print(actions_receveid, "send")
                    s.sendto(pickle.dumps(f"{actions_receveid}?{message_count}"), addr)
                    message_history.append(actions_receveid)
                    if len(message_history) >=151:
                        del message_history[-1]
                    message_count += 1
                    last_action_to = addr
                    actions_receveid = "False"