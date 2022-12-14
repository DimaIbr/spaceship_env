import pygame
import random
import numpy as np
from time import sleep

class Space_Ship_Enviroment:
    def __init__(self):
        # FPS 1000/turn_delay
        self.turn_delay = 10

        self.boot_shoot_delay = 25  # количество ходов

        # размеры окна
        self.width_win = 1000
        self.heigth_win = 1000

        # Стартовая позиция игрока
        self.start_point_x = 100
        self.start_point_y = 100

        # Базовые размеры объектов
        self.person_size = 30
        self.person_defolt = 30
        self.boolet = self.person_defolt // 2
        self.comet_size = self.person_defolt // 2

        # Условия победы
        self.winner_size = self.person_defolt * 5
        self.bots_remain_winner = 1

        # базовые сокрости объектов
        self.speed_move = 10
        self.speed_shoot = self.speed_move * 4
        self.speed_comet = self.speed_move * 2

        # Базовые очки за действия
        self.shoot_k = 2
        self.kill_komet_k = 3

        # Базовое количество ботов
        self.number_of_bots = 6

        self.bots_remain = self.number_of_bots

        self.win = pygame.display.set_mode((self.width_win, self.heigth_win))
        pygame.display.set_caption("Space ships")  # Исправить потом

        self.reset()

    def step(self, action):
        control = self.pars_control(action)
        self.timestamp += 1
        self.win.fill((0, 0, 0))  # очистка поля
        self.spawn_comet()
        self.action_in_game(control)
        self.del_collision_objects()
        self.del_dead_objects()
        return self.observe()[0], self.reward()[0], self.is_running, 0

    def observe(self):
        observation = []
        for bot in self.objects_in_game['bots']:
            observation.append(self.bot_observe(bot))
        return observation

    def reward(self):
        res = []
        for obj in self.objects_in_game['bots']:
            life_time=obj.life_turn
            znach=obj.size*5+life_time-obj.dead*10
            res.append(znach)
        return res

    def reset(self):
        self.objects_in_game = {'comets': [],
                                'bots': [],
                                'boolets': []}
        self.is_running = True
        self.timestamp = 0
        self.dead_bots = {}
        self.spawn_bots(self.number_of_bots)
        return self.observe()[0]

    def display(self):
        for i in self.objects_in_game['comets']:
            pygame.draw.rect(self.win, i.color, (i.x, i.y, i.size, i.size))
        for i in self.objects_in_game['bots']:
            pygame.draw.rect(self.win, i.color, (i.x, i.y, i.size, i.size))
        for i in self.objects_in_game['boolets']:
            pygame.draw.rect(self.win, i.color, (i.x, i.y, i.size, i.size))
        pygame.display.update()# Обновляме изображение
        for event in pygame.event.get(): #реакция на закрытие окна
            if event.type == pygame.QUIT:
                exit()
    def close(self):
        pass

    def spawn_comet(self):
        if random.uniform(0, 1) < 0.98:
            return
        wall = random.choice(['UP','DOWN','LEFT','RIGHT'])
        fullspeed = self.speed_comet * random.randint(1, 3)
        if wall == 'UP':
            y = 0
            x = random.randint(1, self.width_win)
            speed_comet_x = random.randint(0, fullspeed // self.speed_comet) * self.speed_comet
            speed_comet_y = fullspeed - speed_comet_x
        elif wall == 'DOWN':
            y = self.heigth_win
            x = random.randint(1, self.width_win)
            speed_comet_x = random.randint(0, fullspeed // self.speed_comet) * self.speed_comet
            speed_comet_y = -(fullspeed - speed_comet_x)
        elif wall == 'LEFT':
            x = 0
            y = random.randint(1, self.heigth_win)
            speed_comet_y = random.randint(0, fullspeed // self.speed_comet) * self.speed_comet
            speed_comet_x = fullspeed - speed_comet_y
        else:
            x = self.width_win
            y = random.randint(1, self.heigth_win)
            speed_comet_y = random.randint(0, fullspeed // self.speed_comet) * self.speed_comet
            speed_comet_x = -(fullspeed - speed_comet_y)
        self.objects_in_game['comets'].append(
            game_object(x, y, self.comet_size, [speed_comet_x, speed_comet_y], (192, 192, 192), 'comet'))

    def action_in_game(self, control):
        for i in self.objects_in_game['bots']:
            comand_bot_i = control[int(i.name)]
            if comand_bot_i == 'SHOOT':
                i.turn_till_last_shoot = 0
            i.x, i.y, i.face, i.dead = self.action_object(i, comand_bot_i)
            i.turn_till_last_shoot += 1
        if len(self.objects_in_game['bots']) <= 0 or self.timestamp >= 10000:
            self.is_running = False
        for i in range(len(self.objects_in_game['boolets'])):
            if not self.objects_in_game['boolets'][i].is_dead_f():
                self.objects_in_game['boolets'][i].x, self.objects_in_game['boolets'][i].y, self.objects_in_game['boolets'][i].face, \
                self.objects_in_game['boolets'][i].dead, = self.action_object(self.objects_in_game['boolets'][i], self.objects_in_game['boolets'][i].face)
        for i in self.objects_in_game['comets']:
            if not i.is_dead_f():
                i.x, i.y, i.dead = self.comet_movement(i)

    def action_object(self, obj, act):
        # Движение объекта (любого)
        if act == 'LEFT':
            if obj.x > obj.speed:
                obj.x -= obj.speed
                obj.face = 'LEFT'
            else:
                obj.dead = 1
        if act == 'RIGHT':
            if obj.x < self.width_win - obj.size - obj.speed:
                obj.x += obj.speed
                obj.face = 'RIGHT'
            else:
                obj.dead = 1
        if act == 'UP':
            if obj.y > obj.speed:
                obj.y -= obj.speed
                obj.face = 'UP'
            else:
                obj.dead = 1
        if act == 'DOWN':
            if obj.y < self.heigth_win - obj.size - obj.speed:
                obj.y += obj.speed
                obj.face = 'DOWN'
            else:
                obj.dead = 1
        if act == 'SHOOT':
            self.shooted_obj(obj)
        return obj.x, obj.y, obj.face, obj.dead

    def shooted_obj(self, obj):
        diff = obj.size - self.boolet
        if obj.face == 'UP':
            obj.x += (diff) // 2
        elif obj.face == 'DOWN':
            obj.y += diff
            obj.x += (diff) // 2
        elif obj.face == 'LEFT':
            obj.y += (diff) // 2
        else:
            obj.y += (diff) // 2
            obj.x += diff
        boolet_ad = game_object(obj.x, obj.y, self.boolet, self.speed_shoot, (255, 255, 255), 'boolet', face=obj.face, parent=obj.name)
        self.objects_in_game['boolets'].append(boolet_ad)

    def comet_movement(self, obj):
        if obj.speed[0] > 0:
            x_move = 'RIGHT'
        else:
            x_move = 'LEFT'
        if obj.speed[1] > 0:
            y_move = 'DOWN'
        else:
            y_move = 'UP'
        obj.x, obj.y, obj.face, obj.dead = self.action_object(game_object(obj.x, obj.y, obj.size, abs(obj.speed[0]),
                                                                          obj.color, obj.type_ob,
                                                                          face='UP', name='default', dead=obj.dead), x_move)
        obj.x, obj.y, obj.face, obj.dead = self.action_object(game_object(obj.x, obj.y, obj.size, abs(obj.speed[1]),
                                                                          obj.color, obj.type_ob,
                                                                          face='UP', name='default', dead=obj.dead), y_move)
        return obj.x, obj.y, obj.dead

    def del_collision_objects(self):
        for i in self.objects_in_game['comets']:
            self.check_collision(i)
        for i in self.objects_in_game['bots']:
            self.check_collision(i)
        for i in self.objects_in_game['boolets']:
            self.check_collision(i)

    def check_collision(self, i):
        for j in self.objects_in_game['comets']:
            if i != j and ((i.x + i.size >= j.x and i.x <= j.x) and (i.y + i.size >= j.y and i.y <= j.y) or (
                    i.x + i.size >= j.x and i.x <= j.x and i.y + i.size >= j.y + j.size and i.y <= j.y + j.size)) and i.x > 0 and i.y > 0:
                i.dead = 1
                j.dead = 1
        for j in self.objects_in_game['bots']:
            if i.type_ob == 'boolet':
                continue

            if i != j and ((i.x + i.size >= j.x and i.x <= j.x) and (i.y + i.size >= j.y and i.y <= j.y) or (
                    i.x + i.size >= j.x and i.x <= j.x and i.y + i.size >= j.y + j.size and i.y <= j.y + j.size)) and i.x > 0 and i.y > 0:
                i.dead = 1
                j.dead = 1
        for j in self.objects_in_game['boolets']:
            if j.parent == i.name:
                continue

            if i != j and ((i.x + i.size >= j.x and i.x <= j.x) and (i.y + i.size >= j.y and i.y <= j.y) or (
                    i.x + i.size >= j.x and i.x <= j.x and i.y + i.size >= j.y + j.size and i.y <= j.y + j.size)) and i.x > 0 and i.y > 0 and j.parent != i.name:
                if i.type_ob == 'comet':
                    for k in self.objects_in_game['bots']:
                        if k.name == j.parent:
                            k.size += self.comet_size
                elif i.type_ob == 'bot':
                    for k in self.objects_in_game['bots']:
                        if k.name == j.parent:
                            k.size += i.size // 2
                i.dead = 1
                j.dead = 1

    def del_dead_objects(self):
        for i in self.objects_in_game['comets']:
            if i.is_dead_f() or i.dead:
                self.objects_in_game['comets'].pop(self.objects_in_game['comets'].index(i))
        for i in self.objects_in_game['bots']:
            if i.is_dead_f() or i.dead:
                self.dead_bots[i.name] = self.objects_in_game['bots'].pop(self.objects_in_game['bots'].index(i))
            else:
                i.life_turn += 1
        for i in self.objects_in_game['boolets']:
            if i.is_dead_f() or i.dead:
                self.objects_in_game['boolets'].pop(self.objects_in_game['boolets'].index(i))

    def spawn_bots(self, number):
        for i in range(number):
            while True:
                x = random.randint(5, self.width_win - self.person_size - 5)
                y = random.randint(5, self.heigth_win - self.person_size - 5)
                if self.chek_space(x, y, self.person_size):
                    break
            self.objects_in_game['bots'].append(
                                    game_object(x, y, self.person_size, self.speed_move,
                                    (random.randint(1,255),random.randint(1,255),random.randint(1,255)), 'bot', name=str(i))
                                    )

    def chek_space(self, x, y, size):
        for j in self.objects_in_game['comets']:
            if ((x + size >= j.x and x <= j.x) and (y + size >= j.y and y <= j.y) or (
                    x + size >= j.x and x <= j.x and y + size >= j.y + j.size and y <= j.y + j.size)) and x > 0 and y > 0:
                return 0
        for j in self.objects_in_game['bots']:
            if (((x + size >= j.x and x <= j.x) and (y + size >= j.y and y <= j.y)) or (
                    x + size >= j.x and x <= j.x and y + size >= j.y + j.size and y <= j.y + j.size)) and x > 0 and y > 0:
                return 0
        for j in self.objects_in_game['boolets']:
            if ((x + size >= j.x and x <= j.x) and (y + size >= j.y and y <= j.y) or (
                    x + size >= j.x and x <= j.x and y + size >= j.y + j.size and y <= j.y + j.size)) and x > 0 and y > 0:
                return 0
        return 1

    def bot_observe(self, bot):
        def is_under_line(k, b, xy):
            return k*xy[0] + b < xy[1]

        def is_cross(i, k, b):
            leftup = [i.x, i.y]
            leftdown = [i.x, i.y + i.size]
            rightup = [i.x +  i.size, i.y]
            rightdown = [i.x + i.size, i.y + i.size]
            a1 = is_under_line(k, b,leftup)
            a2 = is_under_line(k, b, leftdown)
            a3 = is_under_line(k, b, rightup)
            a4 = is_under_line(k, b, rightdown)
            return (a1 == a2) and (a2 == a3) and (a3 == a4)

        obs = [self.width_win-bot.x, bot.x, self.heigth_win-bot.y, bot.y]
        draw = [0, 0, 0, 0]
        for i in self.objects_in_game['bots']:
            if (i.name==bot.name):
                continue

            if not is_cross(i, 0, bot.y):
                if (bot.x < i.x):
                    obs[0] = min(obs[0], abs(bot.x - i.x))
                    draw[0] = 1
                else:
                    obs[1] = min(obs[1], abs(bot.x - i.x))
                    draw[1] = 1
            b1 = bot.y - 20 * bot.x
            if not is_cross(i, 20, b1):
                if (bot.y < i.y):
                    obs[2] = min(obs[2], ((bot.x - i.x) ** 2 + (bot.y - i.y) ** 2) ** 0.5)
                    draw[2] = 1
                else:
                    obs[3] = min(obs[3], ((bot.x - i.x) ** 2 + (bot.y - i.y) ** 2) ** 0.5)
                    draw[3] = 1

        for i in self.objects_in_game['boolets']:
            if (i.name==bot.name):
                continue

            if not is_cross(i, 0, bot.y):
                if (bot.x < i.x):
                    obs[0] = min(obs[0], abs(bot.x - i.x))
                else:
                    obs[1] = min(obs[1], abs(bot.x - i.x))

            if not is_cross(i, 20, bot.y):
                if (bot.y < i.y):
                    obs[2] = min(obs[2], ((bot.x - i.x) ** 2 + (bot.y - i.y) ** 2) ** 0.5)
                else:
                    obs[3] = min(obs[3], ((bot.x - i.x) ** 2 + (bot.y - i.y) ** 2) ** 0.5)

        for i in self.objects_in_game['comets']:
            if (i.name==bot.name):
                continue

            if not is_cross(i, 0, bot.y):
                if (bot.x < i.x):
                    obs[0] = min(obs[0], abs(bot.x - i.x))
                else:
                    obs[1] = min(obs[1], abs(bot.x - i.x))


            if not is_cross(i, 20, bot.y):
                if (bot.y < i.y):
                    obs[2] = min(obs[2], ((bot.x - i.x) ** 2 + (bot.y - i.y) ** 2) ** 0.5)
                else:
                    obs[3] = min(obs[3], ((bot.x - i.x) ** 2 + (bot.y - i.y) ** 2) ** 0.5)

        pygame.draw.line(self.win, ((255, 255, 255), (0, 255, 255))[draw[0]], (bot.x, bot.y), (1000, bot.y), 2)
        pygame.draw.line(self.win, ((255, 255, 255), (0, 255, 255))[draw[1]], (0, bot.y), (bot.x, bot.y), 2)
        b1 = bot.y - 20 * bot.x
        pygame.draw.line(self.win, ((255, 255, 255), (0, 255, 255))[draw[2]], (bot.x, bot.y), (1000, 1000 * 20 + b1), 2)
        pygame.draw.line(self.win, ((255, 255, 255), (0, 255, 255))[draw[3]], (0, b1), (bot.x, bot.y), 2)

        return obs

    def pars_control(self, action):
        act = ('UP','DOWN','LEFT','RIGHT', 'SHOOT')[np.argmax(action)]
        return [act for _ in range(self.number_of_bots)]



class game_object:
    def __init__(self,position_x,position_y,size,speed,color,type_ob,parent='defolt',name='defoult',face='UP', dead=0):
        self.name=name
        self.x=position_x
        self.y=position_y
        self.dead=dead
        self.size=size
        self.speed=speed
        self.color=color
        self.type_ob=type_ob
        self.life_turn=0
        self.face=face
        self.turn_till_last_shoot=0
        self.parent=parent

    def is_dead_f(self):
        if self.x<0 and self.y<0:
            self.dead=1
            return 1
        else:
            return 0