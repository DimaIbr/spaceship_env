import pygame
import random
import numpy as np
from time import sleep
import math
from SuperNN import MyNNet

class Space_Ship_Enviroment:
    def __init__(self):

        self.Net = MyNNet([4 + 8 * 2 + 4 + 1, 100, 5], ['relu', 'sigmoid'])
        self.Net.set_weights_vector(self.read_weights('best run and shoot 2.txt'))
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
        self.number_of_bots = 5

        self.bots_remain = self.number_of_bots


        self.reset()

    def step(self, action):
        control = self.pars_control(action)
        self.timestamp += 1
        self.win.fill((0, 0, 0))  # очистка поля
        self.spawn_comet()
        self.action_in_game(control)
        self.del_collision_objects()
        self.del_dead_objects()
        return self.norm(self.observe()[0]), self.reward()[0], not self.is_running, 0

    def observe(self):
        # observation = []
        # for bot in self.objects_in_game['bots']:
        #     observation.append(self.bot_observe(bot))
        # return observation
        return [self.bot_observe(self.objects_in_game['bots'][0])]

    def reward(self):
        res = []
        for obj in self.objects_in_game['bots']:
            life_time=obj.life_turn
            znach=obj.size*5+life_time-obj.dead*10
            # res.append(znach)
            res.append(self.timestamp + (obj.size - self.person_defolt) * 5)
        return res

    def reset(self):
        self.win = pygame.display.set_mode((self.width_win, self.heigth_win))
        pygame.display.set_caption("Space ships")  # Исправить потом
        self.objects_in_game = {'comets': [],
                                'bots': [],
                                'boolets': []}
        self.is_running = True
        self.timestamp = 0
        self.dead_bots = {}
        self.spawn_bots(self.number_of_bots)
        return self.observe()[0]

    def render(self):
        self.display()

    def display(self):
        for i in self.objects_in_game['comets']:
            pygame.draw.rect(self.win, i.color, (i.x, i.y, i.size, i.size))
        for i in self.objects_in_game['bots']:
            if i.dead or i.is_dead_f():
                continue
            pygame.draw.rect(self.win, i.color, (i.x, i.y, i.size, i.size))
        for i in self.objects_in_game['boolets']:
            pygame.draw.rect(self.win, i.color, (i.x, i.y, i.size, i.size))
        pygame.display.update() # Обновляме изображение
        for event in pygame.event.get(): #реакция на закрытие окна
            if event.type == pygame.QUIT:
                exit()

    def close(self):
        pass

    def spawn_comet(self):
        if random.uniform(0, 1) < 0.95:
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
        bots_remain = 0
        for i in self.objects_in_game['bots']:
            if not i.dead:
                bots_remain += 1
            elif i.name == '0':
                self.is_running = False
            comand_bot_i = control[int(i.name)]
            if comand_bot_i == 'SHOOT':
                i.turn_till_last_shoot = 0
            i.x, i.y, i.face, i.dead = self.action_object(i, comand_bot_i)
            i.turn_till_last_shoot += 1
        if bots_remain <= 1 or self.timestamp >= 10000:
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
        if i.x < 0 or i.y < 0 or i.x + i.size > self.width_win or i.y + i.size > self.heigth_win:
            i.dead = 1
            pass
        for j in self.objects_in_game['comets']:
            if i != j and ((i.x + i.size >= j.x and i.x <= j.x) and (i.y + i.size >= j.y and i.y <= j.y) or (
                    i.x + i.size >= j.x and i.x <= j.x and i.y + i.size >= j.y + j.size and i.y <= j.y + j.size)) and i.x > 0 and i.y > 0:
                i.dead = 1
                j.dead = 1
        for j in self.objects_in_game['bots']:
            if i.type_ob == 'boolet':
                continue
            if i != j and (
                    (i.x + i.size >= j.x and i.x <= j.x) and (i.y + i.size >= j.y and i.y <= j.y) or
                    (i.x + i.size >= j.x and i.x <= j.x and i.y + i.size >= j.y + j.size and i.y <= j.y + j.size)
                          ) \
                    and i.x > 0 and i.y > 0:
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
                            k.size += i.size // 8
                i.dead = 1
                j.dead = 1

    def del_dead_objects(self):
        for i in self.objects_in_game['comets']:
            if i.is_dead_f() or i.dead:
                self.objects_in_game['comets'].pop(self.objects_in_game['comets'].index(i))
        for i in self.objects_in_game['bots']:
            if not i.is_dead_f() and not i.dead:
                i.life_turn += 1
        for i in self.objects_in_game['boolets']:
            if i.is_dead_f() or i.dead:
                self.objects_in_game['boolets'].pop(self.objects_in_game['boolets'].index(i))

    def spawn_bots(self, number):
        self.objects_in_game['bots'].append(
            game_object(self.width_win / 2, self.width_win / 2, self.person_size, self.speed_move,
                        (255, 255, 255), 'bot', name=str(0))
        )
        for i in range(1, number):
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

    def bot_observe(self, bot, show_lines=True):
        def direction():
            if bot.face == 'LEFT':
                return [1, 0, 0, 0]
            if bot.face == 'RIGHT':
                return [0, 1, 0, 0]
            if bot.face == 'UP':
                return [0, 0, 1, 0]
            if bot.face == 'DOWN':
                return [0, 0, 0, 1]

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

        def sensor(i, alpha):
            k = math.tan(alpha)
            c_x = bot.x + bot.size / 2
            c_y = bot.y + bot.size / 2
            b = c_y - k * c_x
            obs = 0
            if not is_cross(i, k, b):
                obs = math.sqrt((bot.x - i.x) ** 2 + (bot.y - i.y) ** 2)

            if alpha > math.pi / 4 and alpha < 3 * math.pi / 4:
                if (bot.y < i.y):
                    return 0, obs
                else:
                    return obs, 0
            else:
                if (bot.x < i.x):
                    return 0, obs
                else:
                    return obs, 0

        def draw_line(alpha, is1, is2):
            k1 = math.tan(alpha)
            c_x = bot.x + bot.size / 2
            c_y = bot.y + bot.size / 2
            b1 = c_y - k1 * c_x
            pygame.draw.line(self.win, ((255, 255, 255), (255, 0, 255))[bool(is2)], (c_x, c_y), (1000, 1000 * k1 + b1), 2)
            pygame.draw.line(self.win, ((255, 255, 255), (255, 0, 255))[bool(is1)], (0, b1), (c_x, c_y), 2)

        def check_sensors(obj, sens_data, sens_angle, binary):
            assert len(sens_data) == len(sens_angle) * 2
            for i in range(len(sens_angle)):
                a, b = sensor(obj, sens_angle[i])
                if binary:
                    if a: sens_data[2 * i] = 1
                    if b: sens_data[2 * i + 1] = 1
                else:
                    if a: sens_data[2 * i] = max(sens_data[2 * i], a)
                    if b: sens_data[2 * i + 1] = max(sens_data[2 * i + 1], b)

        sensors_angles = [
                          0,
                          99 * math.pi / 200,
                          math.pi / 4,
                          3 * math.pi / 4,

                          math.pi / 8,
                          3 * math.pi / 8,
                          5 * math.pi / 8,
                          7 * math.pi / 8
                          ]
        obs = [self.width_win-bot.x, bot.x, self.heigth_win-bot.y, bot.y]
        comets = [0 for _ in range(len(sensors_angles) * 2)]
        bots = [0 for _ in range(len(sensors_angles) * 2)]
        for i in self.objects_in_game['bots']:
            if (i.name==bot.name):
                continue
            a, b = sensor(i, 0)
            if a:
                obs[0] = max(obs[0], a)
            if b:
                obs[1] = max(obs[1], b)

            a, b = sensor(i, 99 * math.pi / 200)
            if a:
                obs[2] = max(obs[2], a)
            if b:
                obs[3] = max(obs[3], b)
            check_sensors(i, bots, sensors_angles, binary=True)

        for i in self.objects_in_game['boolets']:
            if bot.name == i.parent:
                continue
            check_sensors(i, comets, sensors_angles, binary=False)

        for i in self.objects_in_game['comets']:
            check_sensors(i, comets, sensors_angles, binary=False)

        if show_lines:
            for i in range(len(sensors_angles)):
                draw_line(sensors_angles[i], comets[2 * i], comets[2 * i + 1])
            return obs + comets + bots + direction() + [bot.speed]
        return obs + comets + direction() + [bot.speed]

    def pars_control(self, action):
        act = ('UP','DOWN','LEFT','RIGHT', 'SHOOT')[action]
        list = [act]
        # for i in range(self.number_of_bots - 1):
        #     list.append(random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT', 'SHOOT']))
        for i in range(1, len(self.objects_in_game['bots'])):
            cho = np.argmax(self.Net.forward([self.bot_observe(self.objects_in_game['bots'][i], show_lines=False)])[0][0])
            list.append(('UP','DOWN','LEFT','RIGHT', 'SHOOT')[cho])
        return list

    def norm(self, x):
        y = x.copy()
        n = max(x)
        for i in range(len(x)):
            y[i] = x[i] / n
        return y

    def read_weights(self, filename):
        data = []
        with open(filename, 'r') as fp:
            for line in fp:
                # remove linebreak from a current name
                # linebreak is the last character of each line
                x = line[:-1]

                # add current item to the list
                data.append(float(x))
        return data

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