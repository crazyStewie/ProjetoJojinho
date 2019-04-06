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
        self.number_players = number_players
        self.map_number = map_number
        self.map: Map = None
        self.players = []
        self.passengers = []
        self.MAX_PASSENGERS_REQUESTING = self.number_players//2
        self.passenger_can_request = True
        self.passenger_timer = -1
        self.requesting_passengers = []
        self.get_in_car_timers = []
        self.getting_in_car_players = []
        self.passenger_circles = []
        self.destination_circles = []
        self.tuple_destinations = []
        self.get_out_of_car_timers = []
        self.carriers = []
        with open("../assets/levels/Map%d.pickle" % self.map_number, "rb") as f:
            self.map = pickle.load(f)
        for i in range(125):
            random_sidewalk = math.floor(random()*len(self.map.sidewalks))
            random_position = random()*self.map.sidewalks_length[random_sidewalk]
            random_direction = math.floor(2*random())*2 - 1
            position = Vec2d(self.map.sidewalk_crossings[self.map.sidewalks[random_sidewalk][0]]) + \
                       self.map.get_sidewalk_direction(random_sidewalk)*random_position
            self.passengers.append(Passerby(random_sidewalk, random_position, random_direction,
                                            (position.x, position.y)))
        self.space = pymunk.Space()

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

        self.HUDs = []
        for player_index in range(len(self.players)):
            self.HUDs.append(HUD.HUD(self.players[player_index], (consts.WINDOW_WIDTH/2 - len(self.players)/2 *
                                                                  HUD.HUD_WIDTH + HUD.HUD_WIDTH*player_index, 0)))

    def update(self, dt):
        for player in self.players:
            player.update(dt)
            player.fuel -= dt*0.05
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
        self.space.step(dt)
        for HUD_ in self.HUDs:
            HUD_.update(dt)
        if self.passenger_can_request:
            if self.passenger_timer == -1:
                self.passenger_timer = random()*4 + 3
            else:
                self.passenger_timer -= dt
                if self.passenger_timer <= 0:
                    self.requesting_passengers.append(self.passengers[math.floor(random()*len(self.passengers))])
                    requesting_passenger = self.requesting_passengers[len(self.requesting_passengers) - 1]
                    requesting_passenger.direction = 0
                    position = Vec2d(self.map.sidewalk_first_crossing(requesting_passenger.sidewalk)) + \
                               self.map.get_sidewalk_direction(requesting_passenger.sidewalk) * \
                               requesting_passenger.relative_position
                    circle = pyglet.graphics.vertex_list(32, ("v2f", make_circle(position.x, position.y, 16)),
                                                         ("c3B", (255, 190, 60) * 32))
                    self.passenger_circles.append(circle)
                    self.passenger_can_request = len(self.requesting_passengers) < self.MAX_PASSENGERS_REQUESTING
                    self.passenger_timer = -1
        for requesting_passenger_index in range(len(self.requesting_passengers)):
            requesting_position = Vec2d(
                self.map.sidewalk_first_crossing(
                    self.requesting_passengers[requesting_passenger_index].sidewalk)) + \
                    self.map.get_sidewalk_direction(self.requesting_passengers[
                                                        requesting_passenger_index].sidewalk) * \
                    self.requesting_passengers[requesting_passenger_index].relative_position
            for player_index in range(len(self.players)):
                if requesting_position.get_distance(self.players[player_index].body.position) < 24 \
                        and (len(self.getting_in_car_players) <= requesting_passenger_index
                             or player_index == self.getting_in_car_players[requesting_passenger_index]):
                    if len(self.getting_in_car_players) <= requesting_passenger_index:
                        if requesting_passenger_index == 0:
                            self.getting_in_car_players.append(player_index)
                            self.get_in_car_timers.append(0.5)
                        else:
                            if len(self.getting_in_car_players) == 0:
                                self.getting_in_car_players.append(None)
                                self.get_in_car_timers.append(-1)
                            self.getting_in_car_players.append(player_index)
                            self.get_in_car_timers.append(0.5)
                    else:
                        if self.get_in_car_timers[requesting_passenger_index] == -1:
                            self.getting_in_car_players[requesting_passenger_index] = player_index
                            self.get_in_car_timers[requesting_passenger_index] = 0.5
                        else:
                            if self.get_in_car_timers[requesting_passenger_index] > 0:
                                self.get_in_car_timers[requesting_passenger_index] -= dt
                            else:
                                self.passenger_circles[requesting_passenger_index].delete()
                                self.passenger_circles.pop(requesting_passenger_index)
                                self.passengers.remove(self.requesting_passengers[requesting_passenger_index])
                                self.get_in_car_timers.pop(requesting_passenger_index)
                                self.getting_in_car_players.pop(requesting_passenger_index)
                                self.requesting_passengers.pop(requesting_passenger_index)
                                random_sidewalk = math.floor(random()*len(self.map.sidewalks))
                                random_relative_position = random()*self.map.sidewalks_length[random_sidewalk]
                                position = Vec2d(self.map.sidewalk_first_crossing(random_sidewalk)) + \
                                           self.map.get_sidewalk_direction(random_sidewalk) * \
                                           random_relative_position
                                circle = pyglet.graphics.vertex_list(32, ("v2f", make_circle(position.x, position.y, 16)),
                                                                     ("c3B", (120, 240, 90) * 32))
                                self.destination_circles.append(circle)
                                self.tuple_destinations.append((random_sidewalk, random_relative_position))
                                self.carriers.append(player_index)
                else:
                    if requesting_position.get_distance(self.players[player_index].body.position) > 24 \
                            and (len(self.getting_in_car_players) <= requesting_passenger_index
                                 or player_index == self.getting_in_car_players[requesting_passenger_index]):
                        self.getting_in_car_players.clear()
                        self.get_in_car_timers.clear()
        for carrier_index in range(len(self.carriers)):
            destination_position = Vec2d(
                self.map.sidewalk_first_crossing(self.tuple_destinations[carrier_index][0])) + \
                    self.map.get_sidewalk_direction(self.tuple_destinations[carrier_index][0]) * \
                    self.tuple_destinations[carrier_index][1]
            for player_index in range(len(self.players)):
                if destination_position.get_distance(self.players[player_index].body.position) < 24 \
                        and player_index == self.carriers[carrier_index]:
                    if len(self.get_out_of_car_timers) <= carrier_index:
                        if carrier_index == 0:
                            self.get_out_of_car_timers.append(0.5)
                        else:
                            if len(self.getting_in_car_players) == 0:
                                self.get_out_of_car_timers.append(-1)
                            self.get_out_of_car_timers.append(0.5)
                    else:
                        if self.get_out_of_car_timers[carrier_index] == -1:
                            self.get_out_of_car_timers[carrier_index] = 0.5
                        else:
                            if self.get_out_of_car_timers[carrier_index] > 0:
                                self.get_out_of_car_timers[carrier_index] -= dt
                            else:
                                self.destination_circles[carrier_index].delete()
                                self.destination_circles.pop(carrier_index)
                                self.carriers.pop(carrier_index)
                                position = Vec2d(
                                    self.map.sidewalk_crossings[self.map.sidewalks[
                                        self.tuple_destinations[carrier_index][0]][0]]) + \
                                           self.map.get_sidewalk_direction(
                                               self.tuple_destinations[carrier_index][0]) * \
                                           self.tuple_destinations[carrier_index][1]
                                self.passengers.append(Passerby(self.tuple_destinations[carrier_index][0],
                                                                self.tuple_destinations[carrier_index][1],
                                                                math.floor(random()*2)*2 - 1, (position.x, position.y)))
                                self.get_out_of_car_timers.pop(carrier_index)
                                self.tuple_destinations.pop(carrier_index)
                                self.passenger_can_request = True

    def draw(self):
        self.map.draw_back()
        for passenger in self.passengers:
            passenger.sprite.draw()
        for player in self.players:
            player.draw()
        for HUD_ in self.HUDs:
            HUD_.draw()
        for circle in self.passenger_circles:
            circle.draw(pyglet.gl.GL_LINE_LOOP)
        for circle in self.destination_circles:
            if circle is not None:
                circle.draw(pyglet.gl.GL_LINE_LOOP)
        self.map.draw_front()
