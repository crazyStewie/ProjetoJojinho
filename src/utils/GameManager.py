import pickle
import math
import pymunk
from random import random
from src.game_elements.Passerby import Passerby
from pymunk.vec2d import Vec2d
from src.py_aux import consts

PASSENGER_SPEED = 200


class GameManager:
    def __init__(self, number_players, map_number):
        self.number_players = number_players
        self.map_number = map_number
        self.map = None
        self.players = []
        self.passengers = []
        with open("../assets/levels/Map%d.pickle" % self.map_number, "rb") as f:
            self.map = pickle.load(f)
        for i in range(1):
            random_sidewalk = math.floor(random()*len(self.map.sidewalks))
            random_position = random()*self.map.sidewalks_length[random_sidewalk]
            random_direction = math.floor(2*random())*2 - 1
            position = Vec2d(self.map.sidewalk_crossings[self.map.sidewalks[random_sidewalk][0]]) + \
                       self.map.get_sidewalk_direction(random_sidewalk)*random_position
            self.passengers.append(Passerby(random_sidewalk, random_position, random_direction,
                                            (position.x, position.y)))
        self.space = pymunk.Space()

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

    def update(self, dt):
        for player in self.players:
            player.update(dt)
        for passenger in self.passengers:
            if passenger.relative_position + PASSENGER_SPEED * dt * passenger.direction < 0:
                possibilities = []
                for sidewalk in self.map.sidewalks:
                    if self.map.sidewalk_first_crossing_index(passenger.sidewalk) in sidewalk:
                        possibilities.append(sidewalk)
                random_index = math.floor(random()*len(possibilities))
                print(passenger.sidewalk)
                print(possibilities[random_index])
                if possibilities[random_index].index(self.map.sidewalk_first_crossing_index(passenger.sidewalk)) == 0:
                    print(1)
                    passenger.relative_position = 0
                    passenger.direction = 1
                else:
                    print(2)
                    passenger.relative_position = self.map.sidewalks_length[passenger.sidewalk]
                    passenger.direction = -1
                passenger.sidewalk = self.map.sidewalks.index(possibilities[random_index])
                print(passenger.sidewalk)
            elif passenger.relative_position + PASSENGER_SPEED * dt * passenger.direction > \
                    self.map.sidewalks_length[passenger.sidewalk]:
                possibilities = []
                for sidewalk in self.map.sidewalks:
                    if self.map.sidewalk_second_crossing_index(passenger.sidewalk) in sidewalk:
                        possibilities.append(sidewalk)
                random_index = math.floor(random() * len(possibilities))
                print(passenger.sidewalk)
                print(possibilities[random_index])
                if possibilities[random_index].index(self.map.sidewalk_second_crossing_index(passenger.sidewalk)) == 0:
                    print(3)
                    passenger.relative_position = 0
                    passenger.direction = 1
                else:
                    print(4)
                    passenger.relative_position = self.map.sidewalks_length[passenger.sidewalk]
                    passenger.direction = -1
                passenger.sidewalk = self.map.sidewalks.index(possibilities[random_index])
                print(passenger.sidewalk)
            else:
                passenger.relative_position += PASSENGER_SPEED * dt * passenger.direction
            position = Vec2d(self.map.sidewalk_first_crossing(passenger.sidewalk)) + \
                       self.map.get_sidewalk_direction(passenger.sidewalk) * passenger.relative_position
            passenger.sprite.update(x=position.x, y=position.y)
        self.space.step(dt)

    def draw(self):
        self.map.draw_back()
        for passenger in self.passengers:
            passenger.sprite.draw()
        for player in self.players:
            player.draw()
