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
        self.bullet_count += 1

    def decode(self, data_string=""):
        if not data_string:
            return
        
        try:
            org = data_string
            data_string = data_string.replace("'", "")
            
            # Split the data string and number
            parts = data_string.split("?")
            if len(parts) != 2:
                raise ValueError(f"Invalid data format: missing '?' separator in {data_string}")
            
            data_string, number = parts
            
            # Process the actions
            all_actions = data_string.split(", ")
            actions = []
            
            for action in all_actions:
                if not action:  # Skip empty actions
                    continue
                    
                splitted = action.split(":")
                if len(splitted) != 2:
                    print(f"Warning: Skipping malformed action: {action}")
                    continue
                    
                action_name = splitted[0].replace("'", "")
                action_info_string = splitted[1].replace("'", "")
                action_info_list = action_info_string.split("*")
                
                actions.append((action_name, action_info_list))

            # Process each action
            for act in actions:
                if act[0] == "create":
                    if len(act[1]) < 3:
                        print(f"Warning: Insufficient data for create action: {act}")
                        continue
                        
                    try:
                        # Only create if enemy exists and the rect doesn't already exist
                        rect_id = str(act[1][0])
                        if "enemy" in self.rects and rect_id not in self.rects:
                            self.rects[rect_id] = Rectangle((30*SW, 30*SH), self.rects["enemy"].get_pos(), (0, 0, 0), "09.png")
                            self.rects[rect_id].set_rotation(float(act[1][2]))
                            self.bullet_count += 1
                        elif "enemy" not in self.rects:
                            print("Warning: Cannot create bullet - enemy not initialized yet")
                            # Store this action to process later when enemy is available
                            self.pending_actions = getattr(self, 'pending_actions', [])
                            self.pending_actions.append(act)
                    except ValueError as e:
                        print(f"Warning: Invalid value in create action: {e}")
                        
                elif act[0] == "move":
                    if len(act[1]) < 3:
                        print(f"Warning: Insufficient data for move action: {act}")
                        continue
                        
                    try:
                        rect_id = str(act[1][0])
                        
                        # If this is an enemy initialization message and we don't have an enemy rect yet
                        if rect_id == "enemy" and "enemy" not in self.rects:
                            # Create the enemy rect
                            self.rects["enemy"] = Rectangle((100*SW, 100*SH), (width/2, 100*SH), (0, 0, 0), self.animations["move"][0])
                            print("Enemy rect initialized")
                            
                            # Process any pending actions that were waiting for enemy
                            if hasattr(self, 'pending_actions'):
                                pending = self.pending_actions
                                self.pending_actions = []
                                for pending_act in pending:
                                    print(f"Processing pending action: {pending_act}")
                                    if pending_act[0] == "create":
                                        rect_id = str(pending_act[1][0])
                                        self.rects[rect_id] = Rectangle((30*SW, 30*SH), self.rects["enemy"].get_pos(), (0, 0, 0), "09.png")
                                        self.rects[rect_id].set_rotation(float(pending_act[1][2]))
                                        self.bullet_count += 1
                        
                        # Clean position data
                        pos_data = act[1][1].replace("(", "").replace(")", "")
                        pos = pos_data.split("/")
                        
                        if len(pos) != 2:
                            print(f"Warning: Invalid position format: {pos_data}")
                            continue
                            
                        x_pos = float(pos[0]) * SW
                        y_pos = height - float(pos[1]) * SH
                        rot = float(act[1][2])
                        
                        # Make sure the rect exists
                        if rect_id not in self.rects:
                            print(f"Warning: Unknown rect ID: {rect_id} - creating placeholder")
                            # Create a placeholder object if it's a bullet
                            if rect_id.startswith("bullet"):
                                # For bullets, create a new one at a default position
                                spawn_pos = (width/2, height/2) if "enemy" not in self.rects else self.rects["enemy"].get_pos()
                                self.rects[rect_id] = Rectangle((30*SW, 30*SH), spawn_pos, (0, 0, 0), "09.png")
                                self.bullets[rect_id] = [self.rects[rect_id], 100, rot]
                            continue
                            
                        self.rects[rect_id].set_position(x_pos, y_pos)
                        self.rects[rect_id].set_rotation(-rot)
                        
                    except Exception as excp:
                        print(f"Error processing move action: {excp}")
                        # Request the full message again with retry
                        max_retries = 3
                        retry_count = 0
                        
                        while retry_count < max_retries:
                            try:
                                retry_count += 1
                                print(f"Requesting lost message (attempt {retry_count}/{max_retries})")
                                answ = self.server.send_and_listen(f"req:lostmsg")
                                
                                if not answ or answ == "False":
                                    print("No response or invalid response from server")
                                    break
                                    
                                answ = answ.replace("[", "").replace("]", "")
                                print(f"Received recovery data: {answ}")
                                self.decode(answ)
                                return  # Successfully recovered
                            except Exception as retry_excp:
                                print(f"Recovery attempt {retry_count} failed: {retry_excp}")
                                
                        print("Failed to recover lost message after multiple attempts")
                else:
                    print(f"Warning: Unknown action type: {act[0]}")
                    
            # Update the last message number
            self.last_number = number
            
        except Exception as e:
            print(f"Error decoding message: {e}")
            print(f"Original message: {data_string}")

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


if ip == "":
    ip = "x13-2-1"
server = server_manager(ip)
my_game = game(server)
my_game.main_loop()       