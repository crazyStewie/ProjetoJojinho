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
        if self.gui.mode == "game" and self.current_state == MAIN_MENU:
            self.current_state = IN_GAME
            self.game_manager = GameManager(self.gui.num_players, self.gui.game_level)
            if self.music_player.playing:
                self.music_player.next_source()
        if self.current_state == IN_GAME:
            if not self.music_player.playing:
                self.music_player.queue(self.musics[self.game_manager.music])
                self.music_player.play()
            if self.game_manager.change_music:
                self.music_player.next_source()
                self.music_player.queue(self.musics[self.game_manager.music])
                self.game_manager.change_music = False
                self.music_player.play()
            if self.game_manager.play_sound:
                self.game_manager.play_sound = False
                self.sounds[self.game_manager.sound].play()
            # self.player0.update(dt)
            # self.player1.update(dt)
            # self.space.step(dt)
            self.game_manager.update(dt)
            if self.game_manager.is_over:
                self.current_state = POST_GAME
        if self.current_state == MAIN_MENU:
            if not self.music_player.playing:
                self.music_player.queue(self.musics["top_gear"])
                self.music_player.play()
            self.gui.update(dt)
            if self.gui.play_sound:
                self.gui.play_sound = False
                self.sounds[self.gui.sound].play()
        if self.current_state == POST_GAME:
            if self.music_player.playing:
                self.music_player.next_source()
            if self.post_game_screen is None:
                self.post_game_screen = EndScreen(self.game_manager.get_scores())
                self.game_manager = None
            if self.post_game_screen.play_sound:
                self.sounds["money"].play()
                self.post_game_screen.play_sound = False
            self.post_game_screen.update(dt)
            if self.post_game_screen.is_over:
                if self.music_player.playing:
                    self.music_player.next_source()
                self.post_game_screen.destroy()
                self.post_game_screen = None
                self.current_state = MAIN_MENU
                self.gui.setup_initial_menu(self.gui.params)
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
