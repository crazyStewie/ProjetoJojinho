import pickle
import math
import pymunk
from random import random
from src.game_elements.Passerby import Passerby
from pymunk.vec2d import Vec2d
from src.py_aux import consts
from src.game_elements.Map import Map
from src.game_elements.Player import Player
from src.gui import HUD
PASSENGER_SPEED = 75


class GameManager:
    def __init__(self, number_players, map_number):
        self.number_players = number_players
        self.map_number = map_number
        self.map: Map = None
        self.players = []
        self.passengers = []
        # with open("../assets/levels/test_level.pickle", "rb") as f:
        with open("../assets/levels/Map%d.pickle" % self.map_number, "rb") as f:
            self.map = pickle.load(f)
        for i in range(50):
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
        self.map.generate_body()
        if self.map.col_body is not None:
            self.space.add(self.map.col_body, self.map.col_shapes)
        self.HUDs = []
        for player_index in range(len(self.players)):
            self.HUDs.append(HUD.HUD(self.players[player_index], (consts.WINDOW_WIDTH/2 - len(self.players)/2 *
                                                                  HUD.HUD_WIDTH + HUD.HUD_WIDTH*player_index, 0)))
        self.options = pymunk.pyglet_util.DrawOptions()
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

    def draw(self):
        self.map.draw_back()
        for passenger in self.passengers:
            passenger.sprite.draw()
        for player in self.players:
            player.draw()
        for HUD_ in self.HUDs:
            HUD_.draw()
        self.map.draw_front()
        self.space.debug_draw(self.options)
