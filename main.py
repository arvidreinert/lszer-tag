from setup import *
from rectangle import *
from online_stuff import *
import os

class game():
    def __init__(self,server):
        self.running = True
        self.server = server
        self.rects = {}
        self.animations = {"move":[]}
        self.actions = []
        for i in range(0,20):
            self.animations["move"].append(f"survivor-move_handgun_{i}.png")
        self.rects["player"] = Rectangle((100*SW,100*SH),(width/2*SW,height-100*SW),(0,0,0),self.animations["move"][0])

    def decode(self,data_string=""):
        data_string = data_string.replace("'","")
        all_actions = data_string.split(", ")
        actions = {}
        for action in all_actions:
            splitted = action.split(":")
            x = 0
            for split in splitted:
                splitted[x] = split.replace("'","")
                x += 1
            action_name = splitted[0]
            action_info_string = splitted[1]
            action_info_list = action_info_string.split("*")
            actions[action_name] = action_info_list
        for act in actions:
            if act == "move":
                print(actions[act][1])
                actions[act][1]=actions[act][1].replace("(","")
                actions[act][1]=actions[act][1].replace(")","")
                print(actions[act][1])
                pos = actions[act][1].split("/")
                self.rects[actions[act][0]].set_position(float(pos[0])*SW,height*SH-float(pos[1])*SH)

    def main_loop(self):
        players_count = 0
        pressed_keys = []
        first = True
        fp = False
        while self.running:
            self.actions = []
            if players_count <= 1:
                pygame.display.set_caption(f"player1")
                fp = True
                players_count = self.server.send_and_listen("req peer online")
                players_count = int(players_count)

            if players_count >= 2:
                if first:
                    if fp == False:
                        pygame.display.set_caption(f"player{players_count}")
                    self.rects["enemy"] = Rectangle((100*SW,100*SH),(width/2*SW,100*SH),(0,0,0),self.animations["move"][0])
                    first = False
                answ = server.send_and_listen("req:actio")
                if not answ == "False":
                    print("received data")
                    l_answ = list(answ)
                    del l_answ[0],l_answ[-1]
                    answ = ""
                    for b in l_answ:
                        answ += b
                    l_answ = list(answ)
                    del l_answ[0],l_answ[-1]
                    answ = ""
                    for b in l_answ:
                        answ += b
                    self.decode(answ)


            screen.fill((100,100,100))
            #update things
            self.rects["player"].point_towards(pygame.mouse.get_pos())
            #mocing
            if str(pygame.K_w) in pressed_keys:
                self.rects["player"].move_towards(0.3*SW,True)
            if str(pygame.K_s) in pressed_keys:
                self.rects["player"].move_towards(-0.3*SW,True)
            if str(pygame.K_a) in pressed_keys:
                self.rects["player"].change_position(-0.2*SW,0)
            if str(pygame.K_d) in pressed_keys:
                self.rects["player"].change_position(0.2*SW,0)

            self.rects["player"].change_rotation(90)
            for rect in self.rects:
                self.rects[rect].update(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    pressed_keys.append(str(event.key))
                if event.type == pygame.KEYUP:
                    del pressed_keys[pressed_keys.index(str(event.key))]

            pygame.display.update()
            x = self.rects["player"].get_pos()
            self.actions.append(f"move:enemy*{str((x[0]/SW,x[1]/SH)).replace(", ","/")}")
            if first == False:
                try:
                    server.send(f"actio;{self.actions}")
                except:
                    print(self.actions)


if ip == "":
    ip = "x13-2-1"
server = server_manager(ip)
my_game = game(server)
my_game.main_loop()       