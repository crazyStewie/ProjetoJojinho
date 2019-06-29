from src.gui.GUI import GUI
from src.utils.GameManager import GameManager
import pyglet
from src.utils import Control
from src.game_elements.Player import Player
from src.py_aux import consts
import pymunk
from src.gui.EndScreen import EndScreen
import abc
MAIN_MENU = 0
IN_GAME = 1
POST_GAME = 3


class Game(pyglet.window.Window):
    def __init__(self):
        super(Game, self).__init__(width=consts.WINDOW_WIDTH, height=consts.WINDOW_HEIGHT, fullscreen=True)
        pyglet.clock.schedule_interval(self.update, 1/consts.FPS)
        Control.control.setup(self)
        self.state = MainMenuState
        self.gui = GUI(self)
        self.gui.setup()
        self.game_manager = None
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.frame_count = 0
        self.post_game_screen = None
        self.music_player = pyglet.media.Player()
        pyglet.lib.load_library('avbin')
        pyglet.have_avbin = True
        pyglet.resource.path = ["../assets/sounds"]
        pyglet.resource.reindex()
        self.musics = {"deja_vu": pyglet.resource.media("deja_vu.mp3", streaming=False),
                       "gas_gas_gas": pyglet.resource.media("gas_gas_gas.mp3", streaming=False),
                       "top_gear": pyglet.resource.media("top_gear.mp3", streaming=False)}
        self.sounds = {"select": pyglet.resource.media("select.wav", streaming=False),
                       "change_option": pyglet.resource.media("change_option.wav", streaming=False),
                       "warp": pyglet.resource.media("warp.wav", streaming=False),
                       "call": pyglet.resource.media("call.wav", streaming=False),
                       "deliver": pyglet.resource.media("deliver.wav", streaming=False),
                       "enter": pyglet.resource.media("enter.wav", streaming=False),
                       "invert": pyglet.resource.media("invert.wav", streaming=False),
                       "accelerator": pyglet.resource.media("accelerator.wav", streaming=False),
                       "power_up": pyglet.resource.media("power_up.wav", streaming=False),
                       "oil": pyglet.resource.media("oil.wav", streaming=False),
                       "change_state": pyglet.resource.media("change_state.wav", streaming=False),
                       "wear_off": pyglet.resource.media("wear_off.wav", streaming=False),
                       "power_up_spawn": pyglet.resource.media("power_up_spawn.wav", streaming=False),
                       "money": pyglet.resource.media("money.wav", streaming=False)}
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
        self.state.update(self, dt)
        pass

    def on_draw(self):
        self.clear()
        self.state.on_draw(self)
        self.fps_display.draw()
        pass


class State(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def update(game, dt):
        pass

    @abc.abstractmethod
    def on_draw(game):
        pass


class MainMenuState(State):
    @staticmethod
    def update(game, dt):
        if game.gui.state.get_name() == "game":
            game.state = InGameState
            game.game_manager = GameManager(game.gui.num_players, game.gui.game_level)
            if game.music_player.playing:
                game.music_player.next_source()
        if not game.music_player.playing:
            game.music_player.queue(game.musics["top_gear"])
            game.music_player.play()
        game.gui.update(dt)
        if game.gui.play_sound:
            game.gui.play_sound = False
            game.sounds[game.gui.sound].play()

    @staticmethod
    def on_draw(game):
        game.gui.draw()


class InGameState(State):
    @staticmethod
    def update(game, dt):
        if not game.music_player.playing:
            game.music_player.queue(game.musics[game.game_manager.music])
            game.music_player.play()
        if game.game_manager.change_music:
            game.music_player.next_source()
            game.music_player.queue(game.musics[game.game_manager.music])
            game.game_manager.change_music = False
            game.music_player.play()
        if game.game_manager.play_sound:
            game.game_manager.play_sound = False
            game.sounds[game.game_manager.sound].play()
        # game.player0.update(dt)
        # game.player1.update(dt)
        # game.space.step(dt)
        game.game_manager.update(dt)
        if game.game_manager.is_over:
            game.state = PostGameState

    @staticmethod
    def on_draw(game):
        game.game_manager.draw()


class PostGameState(State):
    @staticmethod
    def update(game, dt):
        if game.music_player.playing:
            game.music_player.next_source()
        if game.post_game_screen is None:
            game.post_game_screen = EndScreen(game.game_manager.get_scores())
            game.game_manager = None
        if game.post_game_screen.play_sound:
            game.sounds["money"].play()
            game.post_game_screen.play_sound = False
        game.post_game_screen.update(dt)
        if game.post_game_screen.is_over:
            if game.music_player.playing:
                game.music_player.next_source()
            game.post_game_screen.destroy()
            game.state = MainMenuState
            game.gui.setup(game.gui.params)

    @staticmethod
    def on_draw(game):
        game.post_game_screen.draw()
