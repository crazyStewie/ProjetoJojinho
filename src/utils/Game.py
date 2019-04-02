from src.gui.GUI import GUI
from src.py_aux import consts
from src.game_elements.Player import Player
import pyglet
import pymunk

MAIN_MENU = 0
IN_GAME = 1
POST_GAME = 3


class Game:
    def __init__(self, window):
        self.current_state = MAIN_MENU
        self.window = window
        self.gui = GUI(self.window)
        self.gui.setup_initial_menu()

        # debug
        self.space = pymunk.Space()

        self.player = Player(0, 100, 100, 0, self.space)

        self.bounding_body = pymunk.Body(1, body_type=pymunk.Body.STATIC)
        self.bounding_segments = \
            (pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(0, 0), pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, 0), 4),
             pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, 0),
                                   pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT), 4),
             pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT),
                                   pymunk.vec2d.Vec2d(0, consts.WINDOW_HEIGHT), 4),
             pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(0, consts.WINDOW_HEIGHT), pymunk.vec2d.Vec2d(0, 0), 4))
        self.space.add(self.bounding_body, self.bounding_segments[0], self.bounding_segments[1], self.bounding_segments[2], self.bounding_segments[3])
        pass

    def update(self, dt):
        if self.gui.mode == "game":
            self.current_state = IN_GAME
            self.player.update(dt)
            self.space.step(dt)
        if self.current_state == MAIN_MENU:
            self.gui.update(dt)
        pass

    def draw(self):
        self.window.clear()
        if self.current_state == MAIN_MENU:
            self.gui.draw()
        if self.current_state == IN_GAME:
            self.player.draw()
        pass
