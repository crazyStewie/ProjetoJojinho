import pickle
import math
import pymunk
import pyglet
from random import random
from src.game_elements.Passerby import Passerby
from pymunk.vec2d import Vec2d
from src.py_aux import consts
from src.game_elements.Map import Map
from src.game_elements.Player import Player
from src.game_elements.PowerUp import PowerUp
from src.gui import HUD
from src.utils import Control
PASSENGER_SPEED = 50


def make_circle(pos_x, pos_y, radius):
    resolution = 32
    verts = []
    radius = Vec2d(radius, 0)
    for i in range(resolution):
        verts += [radius.x + pos_x, radius.y + pos_y]
        radius.rotate_degrees(360 / resolution)
    return verts


class GameManager:
    def __init__(self, number_players, map_number):
        self.is_over = False
        self.passerby_batch = pyglet.graphics.Batch()
        self.number_players = number_players
        self.map_number = map_number
        self.map: Map = None
        self.players = []
        self.passengers = []
        self.MAX_PASSENGERS_REQUESTING = math.ceil(self.number_players/2)
        self.TYPES_POWER_UP = 5
        self.passenger_can_request = True
        self.passenger_timer = -1
        self.money_constant = 0.05
        self.power_up_timer = -1
        self.next_power_up = None
        self.oil_puddles = []
        self.oil_puddles_timers = []
        self.oil_puddles_causers = []
        self.music = "gas_gas_gas"
        self.change_music = False
        self.sound = None
        self.play_sound = False
        self.deja_vu_timer = -1
        self.end_timer = -1
        self.last_collision_players = (0, 0)
        self.last_collision_wall = (0, 0)
        if self.MAX_PASSENGERS_REQUESTING == 1:
            self.requesting_passengers = [-1]
            self.get_in_car_timers = [-1]
            self.getting_in_car_players = [-1]
            self.passenger_circles = [None]
            self.destination_circles = [None]
            self.tuple_destinations = [-1]
            self.run_clocks = [-1]
            self.get_out_of_car_timers = [-1]
            self.carriers = [-1]
            self.power_ups = [None]
            self.indicators = [None]
        else:
            self.requesting_passengers = [-1, -1]
            self.get_in_car_timers = [-1, -1]
            self.getting_in_car_players = [-1, -1]
            self.passenger_circles = [None, None]
            self.destination_circles = [None, None]
            self.tuple_destinations = [-1, -1]
            self.run_clocks = [-1, -1]
            self.get_out_of_car_timers = [-1, -1]
            self.carriers = [-1, -1]
            self.power_ups = [None, None]
            self.indicators = [None, None]
        with open("../assets/levels/Map%d.pickle" % self.map_number, "rb") as f:
            self.map = pickle.load(f)
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        back_img = pyglet.resource.image("maps/back_map" + str(map_number)+".png")
        front_img = pyglet.resource.image("maps/front_map" + str(map_number) + ".png")
        self.map.back_sprite = pyglet.sprite.Sprite(back_img)
        self.map.front_sprite = pyglet.sprite.Sprite(front_img)
        for i in range(100):
            random_sidewalk = math.floor(random()*len(self.map.sidewalks))
            random_position = random()*self.map.sidewalks_length[random_sidewalk]
            random_direction = math.floor(2*random())*2 - 1
            position = Vec2d(self.map.sidewalk_crossings[self.map.sidewalks[random_sidewalk][0]]) + \
                self.map.get_sidewalk_direction(random_sidewalk)*random_position
            self.passengers.append(Passerby(random_sidewalk, random_position, random_direction,
                                            (position.x, position.y),self.passerby_batch))
        self.space = pymunk.Space(True)
        self.space.threads = 4

        for i in range(number_players):
            self.players.append(Player(i, self.map.spawn_positions[i][0], self.map.spawn_positions[i][1], self.map.spawn_rotations[i], self.space))

        self.bounding_body = pymunk.Body(1, body_type=pymunk.Body.STATIC)
        self.bounding_segments = \
            (pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(0, 0),
                                   pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, 0), 4),
             pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, 0),
                                   pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT), 4),
             pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT),
                                   pymunk.vec2d.Vec2d(0, consts.WINDOW_HEIGHT), 4),
             pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(0, consts.WINDOW_HEIGHT),
                                   pymunk.vec2d.Vec2d(0, 0), 4))
        self.space.add(self.bounding_body, self.bounding_segments[0], self.bounding_segments[1],
                       self.bounding_segments[2], self.bounding_segments[3])
        self.map.generate_body()
        if self.map.col_body is not None:
            self.space.add(self.map.col_body, self.map.col_shapes)
        self.HUDs = []
        for player_index in range(len(self.players)):
            self.HUDs.append(HUD.HUD(self.players[player_index], (consts.WINDOW_WIDTH/2 - len(self.players)/2 *
                                                                  HUD.HUD_WIDTH + HUD.HUD_WIDTH*player_index, 0)))
        self.options = pymunk.pyglet_util.DrawOptions()

    def teleport(self, player):
        redo = True
        position = None
        while redo:
            redo = False
            random_street = math.floor(random() * len(self.map.streets))
            random_position = random() * self.map.streets_length[random_street]
            position = Vec2d(self.map.street_first_crossing(random_street)) + \
                       self.map.get_street_direction(random_street) * random_position
            for other in self.players:
                if player != other and position.get_distance(other.body.position) < 60:
                    redo = True
                if player == other and position.get_distance(other.body.position) < 400:
                    redo = True
        player.body.position = position
        self.sound = "warp"
        self.play_sound = True

    def update_passenger_can_request(self, dt):
        if self.passenger_can_request:
            if self.passenger_timer == -1:
                self.passenger_timer = random()*4 + 3
            else:
                self.passenger_timer -= dt
                if self.passenger_timer <= 0:
                    passenger_index = 0
                    while passenger_index < len(self.requesting_passengers) - 1 and \
                            (self.requesting_passengers[passenger_index] != -1 or self.carriers[passenger_index] != -1):
                        passenger_index += 1
                    redo = True
                    requesting_passenger = None
                    position = None
                    while redo:
                        redo = False
                        self.requesting_passengers[passenger_index] = \
                            self.passengers[math.floor(random()*len(self.passengers))]
                        requesting_passenger = self.requesting_passengers[passenger_index]
                        position = Vec2d(self.map.sidewalk_first_crossing(requesting_passenger.sidewalk)) + \
                                   self.map.get_sidewalk_direction(requesting_passenger.sidewalk) * \
                                   requesting_passenger.relative_position
                        for player in self.players:
                            if position.get_distance(player.body.position) < 400:
                                redo = True
                    requesting_passenger.direction = 0
                    circle = pyglet.graphics.vertex_list(32, ("v2f", make_circle(position.x, position.y, 16)),
                                                         ("c3B", (255, 190, 60) * 32))
                    self.passenger_circles[passenger_index] = circle
                    self.passenger_can_request = len(self.requesting_passengers) - \
                                                 self.requesting_passengers.count(-1) + len(self.carriers) - \
                                                 self.carriers.count(-1) < self.MAX_PASSENGERS_REQUESTING
                    self.passenger_timer = -1
                    self.play_sound = True
                    self.sound = "call"

    def update_requesting_passengers(self, dt):
        for requesting_passenger_index in range(len(self.requesting_passengers)):
            if self.requesting_passengers[requesting_passenger_index] == -1:
                continue
            requesting_position = Vec2d(
                self.map.sidewalk_first_crossing(
                    self.requesting_passengers[requesting_passenger_index].sidewalk)) + \
                    self.map.get_sidewalk_direction(self.requesting_passengers[
                                                        requesting_passenger_index].sidewalk) * \
                    self.requesting_passengers[requesting_passenger_index].relative_position
            for player_index in range(len(self.players)):
                if requesting_position.get_distance(self.players[player_index].body.position) < 27 \
                        and (self.getting_in_car_players[requesting_passenger_index] == player_index
                             or self.getting_in_car_players[requesting_passenger_index] == -1) and \
                        self.carriers.count(player_index) == 0 and self.players[player_index].fuel >= 0:
                    if self.get_in_car_timers[requesting_passenger_index] == -1:
                        self.getting_in_car_players[requesting_passenger_index] = player_index
                        self.get_in_car_timers[requesting_passenger_index] = 0.5
                    else:
                        if self.get_in_car_timers[requesting_passenger_index] > 0:
                            self.get_in_car_timers[requesting_passenger_index] -= dt
                        else:
                            initial_sidewalk = self.requesting_passengers[requesting_passenger_index].sidewalk
                            initial_relative_position = \
                                self.requesting_passengers[requesting_passenger_index].relative_position
                            self.passenger_circles[requesting_passenger_index].delete()
                            self.passenger_circles[requesting_passenger_index] = None
                            self.passengers.remove(self.requesting_passengers[requesting_passenger_index])
                            self.get_in_car_timers[requesting_passenger_index] = -1
                            self.getting_in_car_players[requesting_passenger_index] = -1
                            self.requesting_passengers[requesting_passenger_index] = -1
                            random_sidewalk = None
                            random_relative_position = 0
                            position = 0
                            redo = True
                            while redo:
                                random_sidewalk = math.floor(random()*len(self.map.sidewalks))
                                random_relative_position = random()*self.map.sidewalks_length[random_sidewalk]
                                position = Vec2d(self.map.sidewalk_first_crossing(random_sidewalk)) + \
                                           self.map.get_sidewalk_direction(random_sidewalk) * \
                                           random_relative_position
                                redo = position.get_distance(self.players[player_index].body.position) < 600
                            circle = pyglet.graphics.vertex_list(32, ("v2f", make_circle(position.x, position.y, 16)),
                                                                 ("c3B", (120, 240, 90) * 32))
                            self.destination_circles[requesting_passenger_index] = circle
                            self.tuple_destinations[requesting_passenger_index] = \
                                (initial_sidewalk, initial_relative_position, random_sidewalk, random_relative_position)
                            self.carriers[requesting_passenger_index] = player_index
                            pyglet.resource.path = ["../assets/sprites"]
                            pyglet.resource.reindex()
                            ind_image = pyglet.resource.image("indicator.png")
                            ind_image.anchor_x = ind_image.width // 2
                            ind_image.anchor_y = ind_image.height // 2
                            ind_position = Vec2d(self.players[player_index].body.position.x,
                                                 self.players[player_index].body.position.y) + Vec2d(7, 20).\
                                rotated_degrees(-self.players[player_index].sprite.rotation)
                            self.indicators[requesting_passenger_index] = \
                                pyglet.sprite.Sprite(ind_image, ind_position.x, ind_position.y)
                            self.run_clocks[requesting_passenger_index] = 0
                            self.play_sound = True
                            self.sound = "enter"
                else:
                    if requesting_position.get_distance(self.players[player_index].body.position) > 24 \
                            and self.getting_in_car_players[requesting_passenger_index] == player_index:
                        self.getting_in_car_players[requesting_passenger_index] = -1
                        self.get_in_car_timers[requesting_passenger_index] = -1

    def update_carriers(self, dt):
        for carrier_index in range(len(self.carriers)):
            if self.carriers[carrier_index] == -1:
                continue
            destination_position = Vec2d(
                self.map.sidewalk_first_crossing(self.tuple_destinations[carrier_index][2])) + \
                    self.map.get_sidewalk_direction(self.tuple_destinations[carrier_index][2]) * \
                    self.tuple_destinations[carrier_index][3]
            for player_index in range(len(self.players)):
                if destination_position.get_distance(self.players[player_index].body.position) < 24 \
                        and player_index == self.carriers[carrier_index]:
                    if self.get_out_of_car_timers[carrier_index] == -1:
                        self.get_out_of_car_timers[carrier_index] = 0.5
                    else:
                        if self.get_out_of_car_timers[carrier_index] > 0:
                            self.get_out_of_car_timers[carrier_index] -= dt
                        else:
                            self.destination_circles[carrier_index].delete()
                            self.destination_circles[carrier_index] = None
                            self.indicators[carrier_index].delete()
                            self.indicators[carrier_index] = None
                            self.carriers[carrier_index] = -1
                            position = Vec2d(
                                self.map.sidewalk_first_crossing(self.tuple_destinations[carrier_index][2])) + \
                                       self.map.get_sidewalk_direction(self.tuple_destinations[carrier_index][2]) * \
                                       self.tuple_destinations[carrier_index][3]
                            self.passengers.append(Passerby(self.tuple_destinations[carrier_index][2],
                                                            self.tuple_destinations[carrier_index][3],
                                                            math.floor(random()*2)*2 - 1, (position.x, position.y),
                                                            self.passerby_batch))
                            if round(self.tuple_destinations[carrier_index][1] /
                                     self.map.sidewalks_length[self.tuple_destinations[carrier_index][0]]) == 0:
                                initial_crossing = \
                                    self.map.sidewalk_first_crossing_index(self.tuple_destinations[carrier_index][0])
                            else:
                                initial_crossing = \
                                    self.map.sidewalk_second_crossing_index(self.tuple_destinations[carrier_index][0])
                            if round(self.tuple_destinations[carrier_index][3] /
                                     self.map.sidewalks_length[self.tuple_destinations[carrier_index][2]]) == 0:
                                final_crossing = \
                                    self.map.sidewalk_first_crossing_index(self.tuple_destinations[carrier_index][2])
                            else:
                                final_crossing = \
                                    self.map.sidewalk_second_crossing_index(self.tuple_destinations[carrier_index][2])
                            time_penalty = (self.map.distances[initial_crossing][final_crossing] /
                                           self.players[player_index].MAX_SPEED) / self.run_clocks[carrier_index]
                            payment = \
                                math.floor(self.money_constant * self.map.distances[initial_crossing][final_crossing])
                            self.run_clocks[carrier_index] = -1
                            self.players[player_index].money += math.floor(payment*0.6 + payment * 0.4 * time_penalty)
                            self.get_out_of_car_timers[carrier_index] = -1
                            self.tuple_destinations[carrier_index] = -1
                            self.passenger_can_request = True
                            self.play_sound = True
                            self.sound = "deliver"

    def update_power_ups(self, dt):
        for player in self.players:
            for power_up_index in range(len(self.power_ups)):
                if self.power_ups[power_up_index] is None:
                    continue
                if Vec2d(self.power_ups[power_up_index].sprite.position).get_distance(player.body.position) < 32 and \
                        player.power_up is None:
                    player.power_up = self.power_ups[power_up_index]
                    self.power_ups[power_up_index] = None
                    self.play_sound = True
                    self.sound = "power_up"
                    break
        if len(self.power_ups) - self.power_ups.count(None) == 2*self.number_players:
            return
        if self.next_power_up is None:
            random_power_up = math.floor(random()*self.TYPES_POWER_UP)
            self.next_power_up = PowerUp(random_power_up)
            self.power_up_timer = random()*(self.next_power_up.time_range[1] - self.next_power_up.time_range[0]) + \
                                  self.next_power_up.time_range[0]
            return
        if self.power_up_timer > 0:
            self.power_up_timer -= dt
            return
        random_street = math.floor(random()*len(self.map.streets))
        random_relative_position = random()*self.map.streets_length[random_street]
        position = Vec2d(self.map.street_first_crossing(random_street)) + \
                   self.map.get_street_direction(random_street) * random_relative_position
        self.next_power_up.sprite.update(x=position.x, y=position.y)
        self.power_ups.append(self.next_power_up)
        self.power_up_timer = -1
        self.next_power_up = None
        self.play_sound = True
        self.sound = "power_up_spawn"

    def check_power_ups(self, dt):
        if self.deja_vu_timer != -1:
            if self.deja_vu_timer > 0:
                self.deja_vu_timer -= dt
            else:
                self.deja_vu_timer = -1
                self.change_music = True
                self.music = "gas_gas_gas"
        for oil_puddle_timer_index in range(len(self.oil_puddles_timers)):
            if self.oil_puddles_timers[oil_puddle_timer_index] > 0:
                self.oil_puddles_timers[oil_puddle_timer_index] -= dt
            else:
                self.oil_puddles_timers.pop(oil_puddle_timer_index)
                self.oil_puddles.pop(oil_puddle_timer_index)
                self.oil_puddles_causers.pop(oil_puddle_timer_index)
                break
        for player_index in range(len(self.players)):
            if Control.control.just_pressed("Power-up%d" % player_index) and \
                    self.players[player_index].power_up is not None:
                if self.players[player_index].power_up.name == "accelerator":
                    self.players[player_index].accelerator_bonus = True
                    self.players[player_index].accelerator_timer = 1.5
                    self.play_sound = True
                    self.sound = "accelerator"
                elif self.players[player_index].power_up.name == "oil":
                    pyglet.resource.path = ["../assets/sprites"]
                    pyglet.resource.reindex()
                    oil_image = pyglet.resource.image("spilled_oil.png")
                    oil_image.anchor_x = oil_image.width // 2
                    oil_image.anchor_y = oil_image.height // 2
                    self.oil_puddles.append(pyglet.sprite.Sprite(oil_image, self.players[player_index].body.position.x,
                                                                 self.players[player_index].body.position.y))
                    self.oil_puddles_timers.append(20)
                    self.oil_puddles_causers.append(player_index)
                    self.play_sound = True
                    self.sound = "oil"
                elif self.players[player_index].power_up.name == "invert":
                    self.players[player_index].apply_invert = True
                    self.players[player_index].invert_timer = 3
                    self.play_sound = True
                    self.sound = "change_state"
                elif self.players[player_index].power_up.name == "teleport":
                    self.players[player_index].apply_teleport = True
                    self.players[player_index].teleport_timer = 3
                    self.play_sound = True
                    self.sound = "change_state"
                elif self.players[player_index].power_up.name == "self_teleport":
                    self.teleport(self.players[player_index])
                self.players[player_index].power_up = None
            for oil_puddle_index in range(len(self.oil_puddles)):
                if Vec2d(self.oil_puddles[oil_puddle_index].position).\
                        get_distance(self.players[player_index].body.position) < 35 and \
                        player_index != self.oil_puddles_causers[oil_puddle_index]:
                    self.players[player_index].is_oiled = True
                    self.players[player_index].oiled_timer = 20
                    self.change_music = True
                    self.music = "deja_vu"
                    self.deja_vu_timer = 35
        for player_index_1 in range(len(self.players)):
            for player_index_2 in range(len(self.players)):
                if player_index_1 < player_index_2:
                    if len(self.players[player_index_1].poly
                                   .shapes_collide(self.players[player_index_2].poly).points) != 0:
                        if self.players[player_index_1].apply_invert:
                            self.players[player_index_2].is_inverted = True
                            self.players[player_index_2].inverted_timer = 7
                            self.players[player_index_1].apply_invert = False
                            self.players[player_index_1].invert_timer = -1
                            self.play_sound = True
                            self.sound = "invert"
                        if self.players[player_index_2].apply_invert:
                            self.players[player_index_1].is_inverted = True
                            self.players[player_index_1].inverted_timer = 7
                            self.players[player_index_2].apply_invert = False
                            self.players[player_index_2].invert_timer = -1
                            self.play_sound = True
                            self.sound = "invert"
                        if self.players[player_index_1].apply_teleport:
                            self.teleport(self.players[player_index_2])
                            self.players[player_index_1].apply_teleport = False
                            self.players[player_index_1].teleport_timer = -1
                        if self.players[player_index_2].apply_teleport:
                            self.teleport(self.players[player_index_1])
                            self.players[player_index_2].apply_teleport = False
                            self.players[player_index_2].teleport_timer = -1

    def update(self, dt):
        self.space.step(dt)
        for player in self.players:
            player.update(dt)
            if player.wear_off:
                self.play_sound = True
                self.sound = "wear_off"
                player.wear_off = False
        for passenger in self.passengers:
            passenger.relative_position += PASSENGER_SPEED * dt * passenger.direction
            if passenger.relative_position < 0:
                possibilities = []
                current_crossing = self.map.sidewalks[passenger.sidewalk][0]
                for i in range(len(self.map.sidewalks)):
                    if current_crossing in self.map.sidewalks[i] and i != passenger.sidewalk:
                        possibilities.append(i)
                random_index = math.floor(random()*len(possibilities))
                new_sidewalk = possibilities[random_index]
                if current_crossing == self.map.sidewalks[new_sidewalk][0]:
                    passenger.relative_position = 0
                    passenger.direction = 1
                else:
                    passenger.relative_position = self.map.sidewalks_length[new_sidewalk]
                    passenger.direction = -1
                passenger.sidewalk = new_sidewalk
            elif passenger.relative_position > self.map.sidewalks_length[passenger.sidewalk]:
                possibilities = []
                current_crossing = self.map.sidewalks[passenger.sidewalk][1]
                for i in range(len(self.map.sidewalks)):
                    if current_crossing in self.map.sidewalks[i] and i != passenger.sidewalk:
                        possibilities.append(i)
                random_index = math.floor(random() * len(possibilities))
                new_sidewalk = possibilities[random_index]
                if current_crossing == self.map.sidewalks[new_sidewalk][0]:
                    passenger.relative_position = 0
                    passenger.direction = 1
                else:
                    passenger.relative_position = self.map.sidewalks_length[new_sidewalk]
                    passenger.direction = -1
                passenger.sidewalk = new_sidewalk
            position = Vec2d(self.map.sidewalk_first_crossing(passenger.sidewalk)) + \
                       self.map.get_sidewalk_direction(passenger.sidewalk) * passenger.relative_position
            passenger.sprite.update(x=position.x, y=position.y)

        for HUD_ in self.HUDs:
            HUD_.update(dt)
        self.update_passenger_can_request(dt)
        self.update_requesting_passengers(dt)
        self.update_carriers(dt)
        self.update_power_ups(dt)
        self.check_power_ups(dt)
        for clock_index in range(len(self.run_clocks)):
            if self.run_clocks[clock_index] != -1:
                self.run_clocks[clock_index] += dt
        for indicator_index in range(len(self.indicators)):
            if self.indicators[indicator_index] is not None:
                ind_position = Vec2d(self.players[self.carriers[indicator_index]].body.position.x,
                                     self.players[self.carriers[indicator_index]].body.position.y) + Vec2d(7, 20). \
                                   rotated_degrees(-self.players[self.carriers[indicator_index]].sprite.rotation)
                self.indicators[indicator_index].update(ind_position.x, ind_position.y)
        for player_index in range(len(self.players)):
            if self.players[player_index].fuel <= 0:
                if self.carriers.count(player_index) > 0:
                    carrier_index = self.carriers.index(player_index)
                    self.carriers[carrier_index] = -1
                    self.destination_circles[carrier_index].delete()
                    self.destination_circles[carrier_index] = None
                    self.indicators[carrier_index].delete()
                    self.indicators[carrier_index] = None
                    self.run_clocks[carrier_index] = -1
                    self.get_out_of_car_timers[carrier_index] = -1
                    self.tuple_destinations[carrier_index] = -1
                    self.passenger_can_request = True
        out_count = 0
        for player in self.players:
            if player.fuel <= 0:
                out_count += 1
            if out_count == self.number_players and self.end_timer == -1:
                self.end_timer = 0.5
        if self.end_timer != -1:
            if self.end_timer > 0:
                self.end_timer -= dt
            else:
                self.end_timer = -1
                self.is_over = True

    def get_scores(self):
        scores = []
        for p in self.players:
            scores += [p.money]
        return scores

    def draw(self):
        self.map.draw_back()
        #self.space.debug_draw(self.options)
        #for passenger in self.passengers:
        #    passenger.sprite.draw()
        self.passerby_batch.draw()
        for player in self.players:
            player.draw()
        self.map.draw_front()
        for HUD_ in self.HUDs:
            HUD_.draw()
        for circle in self.passenger_circles:
            if circle is not None:
                circle.draw(pyglet.gl.GL_LINE_LOOP)
        for circle in self.destination_circles:
            if circle is not None:
                circle.draw(pyglet.gl.GL_LINE_LOOP)
        for power_up in self.power_ups:
            if power_up is not None:
                power_up.sprite.draw()
        for indicator in self.indicators:
            if indicator is not None:
                indicator.draw()
        for oil_puddle in self.oil_puddles:
            oil_puddle.draw()

