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
from src.gui import HUD
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
        self.passerby_batch = pyglet.graphics.Batch()
        self.number_players = number_players
        self.map_number = map_number
        self.map: Map = None
        self.players = []
        self.passengers = []
        self.MAX_PASSENGERS_REQUESTING = self.number_players//2
        self.passenger_can_request = True
        self.passenger_timer = -1
        if self.MAX_PASSENGERS_REQUESTING == 1:
            self.requesting_passengers = [-1]
            self.get_in_car_timers = [-1]
            self.getting_in_car_players = [-1]
            self.passenger_circles = [None]
            self.destination_circles = [None]
            self.tuple_destinations = [-1]
            self.get_out_of_car_timers = [-1]
            self.carriers = [-1]
        else:
            self.requesting_passengers = [-1, -1]
            self.get_in_car_timers = [-1, -1]
            self.getting_in_car_players = [-1, -1]
            self.passenger_circles = [None, None]
            self.destination_circles = [None, None]
            self.tuple_destinations = [-1, -1]
            self.get_out_of_car_timers = [-1, -1]
            self.carriers = [-1, -1]
        with open("../assets/levels/Map%d.pickle" % self.map_number, "rb") as f:
            self.map = pickle.load(f)
        for i in range(500):
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
            self.players.append(Player(i, 100, 100+50*i, 0, self.space))

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

    def update_passenger_can_request(self, dt):
        if self.passenger_can_request:
            if self.passenger_timer == -1:
                self.passenger_timer = random()*4 + 3
            else:
                self.passenger_timer -= dt
                if self.passenger_timer <= 0:
                    passenger_index = 0
                    while passenger_index < len(self.requesting_passengers) - 1 and \
                            self.requesting_passengers[passenger_index] != -1:
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
                if requesting_position.get_distance(self.players[player_index].body.position) < 24 \
                        and (self.getting_in_car_players[requesting_passenger_index] == player_index
                             or self.getting_in_car_players[requesting_passenger_index] == -1) and \
                        self.carriers.count(player_index) == 0:
                    if self.get_in_car_timers[requesting_passenger_index] == -1:
                        self.getting_in_car_players[requesting_passenger_index] = player_index
                        self.get_in_car_timers[requesting_passenger_index] = 0.5
                    else:
                        if self.get_in_car_timers[requesting_passenger_index] > 0:
                            self.get_in_car_timers[requesting_passenger_index] -= dt
                        else:
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
                                (random_sidewalk, random_relative_position)
                            self.carriers[requesting_passenger_index] = player_index
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
                self.map.sidewalk_first_crossing(self.tuple_destinations[carrier_index][0])) + \
                    self.map.get_sidewalk_direction(self.tuple_destinations[carrier_index][0]) * \
                    self.tuple_destinations[carrier_index][1]
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
                            self.carriers[carrier_index] = -1
                            position = Vec2d(
                                self.map.sidewalk_crossings[self.map.sidewalks[
                                    self.tuple_destinations[carrier_index][0]][0]]) + \
                                       self.map.get_sidewalk_direction(
                                           self.tuple_destinations[carrier_index][0]) * \
                                       self.tuple_destinations[carrier_index][1]
                            self.passengers.append(Passerby(self.tuple_destinations[carrier_index][0],
                                                            self.tuple_destinations[carrier_index][1],
                                                            math.floor(random()*2)*2 - 1, (position.x, position.y),
                                                            self.passerby_batch))
                            self.get_out_of_car_timers[carrier_index] = -1
                            self.tuple_destinations[carrier_index] = -1
                            self.passenger_can_request = True

    def update(self, dt):
        self.space.step(dt)
        for player in self.players:
            player.update(dt)
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
        self.map.draw_front()
