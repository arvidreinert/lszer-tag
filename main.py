from setup import *
from rectangle import *
from online_stuff import *
import os

class game():
    def __init__(self,server):
        self.last_number = 0
        self.running = True
        self.bullet_count = 0
        self.count = 0
        self.server = server
        self.rects = {}
        self.bullets = {}
        self.animations = {"move":[]}
        self.actions = []
        for i in range(0,20):
            self.animations["move"].append(f"survivor-move_handgun_{i}.png")
        self.rects["player"] = Rectangle((100*SW,100*SH),(round(random.uniform(100*SW,width-100*SW),2),height-100*SH),(0,0,0),self.animations["move"][0])
    
    def make_bullet(self):
        name = f"bullet{self.bullet_count}"
        self.rects[name] = Rectangle((30*SW,30*SH),self.rects["player"].get_pos(),(0,0,0),"09.png")
        self.rects[name].set_rotation(self.rects["player"].rotation-90)
        self.bullets[name] = [self.rects[name],100,self.rects["player"].rotation-90]
        self.actions.append(f"create:{name}*100*{self.rects["player"].rotation-90}")
        print("creat:",name,self.actions)
        self.bullet_count += 1

    def decode(self,data_string=""):
        print(data_string)
        org = data_string
        data_string = data_string.replace("'","")
        data_string,number = data_string.split("?")
        all_actions = data_string.split(", ")
        actions = []
        for action in all_actions:
            splitted = action.split(":")
            x = 0
            for split in splitted:
                splitted[x] = split.replace("'","")
                x += 1
            action_name = splitted[0]
            action_info_string = splitted[1]
            action_info_list = action_info_string.split("*")
            actions.append((action_name,action_info_list))

        #print("acts:",actions)
        for act in actions:
            if act[0] == "create":
                self.rects[str(act[1][0])] = Rectangle((30*SW,30*SH),self.rects["enemy"].get_pos(),(0,0,0),"09.png")
                self.rects[str(act[1][0])].set_rotation(float(act[1][2]))
                self.bullet_count += 1
            elif act[0] == "move":
                try:
                    print(act[1])
                    act[1][1]=act[1][1].replace("(","")
                    act[1][1]=act[1][1].replace(")","")
                    rot = act[1][2]
                    pos = act[1][1].split("/")
                    self.rects[str(act[1][0])].set_position(float(pos[0])*SW,height-float(pos[1])*SH)
                    self.rects[str(act[1][0])].set_rotation(-float(rot))
                except Exception as excp:
                    answ = server.send_and_listen(f"req:lostmsg/{self.last_number}.{number}")
                    print("debug error:",answ)
                    msgs = answ.split("=")
                    del msgs[-1]
                    print(excp)
                    for msg in msgs:
                        if "create" in msg:
                            self.decode(msg)
                            break
                    self.decode(org)
        self.last_number = number

    def main_loop(self):
        players_count = 0
        pressed_keys = []
        first = True
        fp = False
        while self.running:
            clock.tick(30)
            if self.count > 0:
                self.count -= 1
            self.actions = []
            pygame.display.set_caption(f"{clock.get_fps()}")
            if players_count <= 1:
                pygame.display.set_caption(f"player1")
                fp = True
                players_count = self.server.send_and_listen("req peer online")
                players_count = int(players_count)

            if players_count >= 2:
                if first:
                    if fp == False:
                        pygame.display.set_caption(f"player2")
                    self.rects["enemy"] = Rectangle((100*SW,100*SH),(width/2,100*SH),(0,0,0),self.animations["move"][0])
                    first = False
                answ = server.send_and_listen("req:actio")
                if not answ == "False":
                    print(answ)
                    answ = answ.replace("[","")
                    answ = answ.replace("]","")
                    self.decode(answ)


            screen.fill((100,100,100))
            #update things
            self.rects["player"].point_towards(pygame.mouse.get_pos())
            #mocing
            if str(pygame.K_w) in pressed_keys:
                self.rects["player"].move_towards(0.5*SW,True)
            if str(pygame.K_s) in pressed_keys:
                self.rects["player"].move_towards(-0.5*SW,True)
            if str(pygame.K_a) in pressed_keys:
                self.rects["player"].change_position(-0.4*SW,0)
            if str(pygame.K_d) in pressed_keys:
                self.rects["player"].change_position(0.4*SW,0)

            self.rects["player"].change_rotation(90)
            for rect in self.rects:
                self.rects[rect].update(screen)
            tdlet = []
            for bullet in self.bullets:
                if self.bullets[bullet][1] > 0:
                    self.bullets[bullet][0].move_towards(2*SW,True)
                    self.bullets[bullet][1] -= 1
                    self.bullets[bullet][0].update(screen)
                    x = self.bullets[bullet][0].get_pos()
                    self.actions.append(f"move:{bullet}*{str((x[0]/SW,x[1]/SH)).replace(", ","/")}*{str(self.rects[bullet].rotation)}")
                else:
                    self.bullets[bullet][0].kill()
                    tdlet.append(bullet)
            for dlt in tdlet:
                del self.bullets[dlt]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    pressed_keys.append(str(event.key))
                if event.type == pygame.KEYUP:
                    del pressed_keys[pressed_keys.index(str(event.key))]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.count == 0:
                        self.make_bullet()
                        self.count = 40

            pygame.display.update()
            x = self.rects["player"].get_pos()
            self.actions.append(f"move:enemy*{str((x[0]/SW,x[1]/SH)).replace(", ","/")}*{str(self.rects["player"].rotation)}")
            if first == False:
                server.send(f"actio;{self.actions}")
                print("sended_acts:",self.actions)


if ip == "":
    ip = "x13-2-1"
server = server_manager(ip)
my_game = game(server)
my_game.main_loop()       