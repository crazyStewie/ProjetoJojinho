from src.gui.GUI import GUI
from src.utils.GameManager import GameManager
import pyglet
from src.utils import Control
from src.game_elements.Player import Player
from src.py_aux import consts
import pymunk
from src.gui.EndScreen import EndScreen
MAIN_MENU = 0
IN_GAME = 1
POST_GAME = 3


class Game(pyglet.window.Window):
    def __init__(self):
        super(Game, self).__init__(width=consts.WINDOW_WIDTH, height=consts.WINDOW_HEIGHT, fullscreen=True)
        pyglet.clock.schedule_interval(self.update, 1/consts.FPS)
        Control.control.setup(self)
        self.current_state = MAIN_MENU
        self.gui = GUI(self)
        self.gui.setup_initial_menu()
        self.game_manager = None
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.frame_count = 0
        self.post_game_screen = None
        # debug
        # self.space = pymunk.Space()
        #
        # self.player0 = Player(0, 100, 100, 0, self.space)
        # self.player1 = Player(1, 100, 100, 0, self.space)
        #
        # self.bounding_body = pymunk.Body(1, body_type=pymunk.Body.STATIC)
        # self.bounding_segments = \
        #     (pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(0, 0), pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, 0), 4),
        #      pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, 0),
        #                            pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT), 4),
        #      pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT),
        #                            pymunk.vec2d.Vec2d(0, consts.WINDOW_HEIGHT), 4),
        #      pymunk.shapes.Segment(self.bounding_body, pymunk.vec2d.Vec2d(0, consts.WINDOW_HEIGHT), pymunk.vec2d.Vec2d(0, 0), 4))
        # self.space.add(self.bounding_body, self.bounding_segments[0], self.bounding_segments[1], self.bounding_segments[2], self.bounding_segments[3])
        pass

    def update(self, dt):
        self.frame_count += 1
        Control.control.update(self)
        if dt > 1/10:
            print("on frame : " + str(self.frame_count))
            print("delta = " + str(dt))
            print("fps   = " + str(1/dt))
            dt = 1/10
        if self.gui.mode == "game" and self.current_state != IN_GAME:
            self.current_state = IN_GAME
            self.game_manager = GameManager(self.gui.num_players, self.gui.game_level)
        if self.current_state == IN_GAME:
            # self.player0.update(dt)
            # self.player1.update(dt)
            # self.space.step(dt)
            self.game_manager.update(dt)
            self.gui.update(dt)
        if self.current_state == MAIN_MENU:
            self.gui.update(dt)
        if self.current_state == POST_GAME:
            if self.post_game_screen is None:
                self.post_game_screen = EndScreen()
            self.post_game_screen.update(dt)
        pass

    def on_draw(self):
        self.clear()
        if self.current_state == MAIN_MENU:
            self.gui.draw()
        if self.current_state == IN_GAME:
            self.game_manager.draw()
            # self.player0.draw()
            # self.player1.draw()
        if self.current_state == POST_GAME:
            self.post_game_screen.draw()
        self.fps_display.draw()
        pass
