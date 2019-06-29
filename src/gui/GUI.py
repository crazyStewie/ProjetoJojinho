from src.gui.Button import Button
from src.gui.Selector import Selector
from src.gui.ButtonIdentifier import ButtonIdentifier
from src.py_aux import consts
import pyglet
from src.utils import Control
import abc


class GUI:
    def __init__(self, window):
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.active_elements = []
        self.passive_elements = []
        self.config_params = None
        self.focus = -1
        self.window = window
        self.state = InitialSetup
        self.game_level = 1
        self.num_players = 2
        self.params = None
        self.play_sound = False
        self.sound = None

    def set_state(self, state):
        self.state = state

    def setup(self, params=None):
        self.state.setup(gui=self, params=params)

    @staticmethod
    def draw_box(corner1, corner2):
        pyglet.graphics.draw(5, pyglet.gl.GL_LINE_STRIP, ("v2f", (corner1[0], corner1[1],
                                                                  corner2[0], corner1[1],
                                                                  corner2[0], corner2[1],
                                                                  corner1[0], corner2[1],
                                                                  corner1[0], corner1[1])))

    def update(self, dt):
        if Control.control.just_released("ui_up"):
            self.focus = max(0, self.focus - 1)
            self.sound = "change_option"
            self.play_sound = True
        elif Control.control.just_released("ui_down"):
            if self.focus < len(Control.control.joysticks)*5 or self.state.get_name() != "config":
                self.focus = min(len(self.active_elements) - 1, self.focus + 1)
                self.sound = "change_option"
                self.play_sound = True
        for index, elem in enumerate(self.active_elements):
            if index == self.focus:
                elem.is_focused = True
            else:
                elem.is_focused = False
            elem.update(dt)

    def draw(self):
        for elem in self.passive_elements:
            elem.draw()
        for elem in self.active_elements:
            elem.draw()
        if len(self.active_elements) > 0:
            corner1 = (self.active_elements[self.focus].x -
                       self.active_elements[self.focus].default_sprite.width//2 - consts.BOX_MARGIN,
                       self.active_elements[self.focus].y -
                       self.active_elements[self.focus].default_sprite.height // 2 - consts.BOX_MARGIN)
            corner2 = (self.active_elements[self.focus].x +
                       self.active_elements[self.focus].default_sprite.width // 2 + consts.BOX_MARGIN,
                       self.active_elements[self.focus].y +
                       self.active_elements[self.focus].default_sprite.height // 2 + consts.BOX_MARGIN)
            self.draw_box(corner1, corner2)


class SetupState(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def setup(gui, params=None):
        pass

    @abc.abstractmethod
    def get_name():
        pass


class InitialSetup(SetupState):
    @staticmethod
    def setup(gui, params=None):
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        if params is not None:
            gui.params = params
            gui.active_elements = [Button("start", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 250])], gui=gui),
                                    Selector("level", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 100])],
                                             value=params[0], gui=gui),
                                    Selector("players", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -50])],
                                             value=params[1], gui=gui),
                                    Button("settings", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -200])],
                                           gui=gui),
                                    Button("quit", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -350])], gui=gui,
                                           window=gui.window)]
        else:
            gui.active_elements = [Button("start", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 250])], gui=gui),
                                    Selector("level", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 100])], gui=gui),
                                    Selector("players", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -50])],
                                             gui=gui),
                                    Button("settings", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -200])],
                                           gui=gui),
                                    Button("quit", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -350])], gui=gui,
                                           window=gui.window)]
        gui.passive_elements = \
            [pyglet.sprite.Sprite(pyglet.resource.image("background.png"))]
        gui.focus = 0

    @staticmethod
    def get_name():
        return "initial"


class ConfigSetup(SetupState):
    @staticmethod
    def setup(gui, params=None):
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        if params is None:
            gui.active_elements = \
                [Button("return", [0 * consts.WINDOW_WIDTH / 4 + 200, 6 * consts.WINDOW_HEIGHT / 7 + 75], gui=gui)]
            gui.passive_elements = \
                [pyglet.sprite.Sprite(pyglet.resource.image("background.png"))]
            for i in range(4):
                gui.active_elements += \
                    [ButtonIdentifier("Up", [i * consts.WINDOW_WIDTH / 4 + 200, 4 * consts.WINDOW_HEIGHT / 7 + 100], i,
                                      gui=gui),
                     ButtonIdentifier("Down", [i * consts.WINDOW_WIDTH / 4 + 200, 3 * consts.WINDOW_HEIGHT / 7 + 100],
                                      i,
                                      gui=gui),
                     ButtonIdentifier("Left", [i * consts.WINDOW_WIDTH / 4 + 200, 2 * consts.WINDOW_HEIGHT / 7 + 100],
                                      i,
                                      gui=gui),
                     ButtonIdentifier("Right", [i * consts.WINDOW_WIDTH / 4 + 200, 1 * consts.WINDOW_HEIGHT / 7 + 100],
                                      i,
                                      gui=gui),
                     ButtonIdentifier("Power-up",
                                      [i * consts.WINDOW_WIDTH / 4 + 200, 0 * consts.WINDOW_HEIGHT / 7 + 100], i,
                                      gui=gui, is_button=True)]
                if i < len(Control.control.joysticks):
                    color = (255, 255, 255, 255)
                else:
                    color = (255, 0, 0, 255)
                gui.passive_elements += \
                    [pyglet.text.Label("Joystick %d" % i, x=i * consts.WINDOW_WIDTH / 4 + 200,
                                       y=5 * consts.WINDOW_HEIGHT / 7 + 100,
                                       anchor_x="center", anchor_y="center", color=color, font_size=40)]
        else:
            gui.active_elements = \
                [Button("return", [0 * consts.WINDOW_WIDTH / 4 + 200, 6 * consts.WINDOW_HEIGHT / 7 + 75], gui=gui)]
            gui.passive_elements = \
                [pyglet.sprite.Sprite(pyglet.resource.image("background.png"))]
            for i in range(4):
                gui.active_elements += \
                    [ButtonIdentifier("Up", [i * consts.WINDOW_WIDTH / 4 + 200, 4 * consts.WINDOW_HEIGHT / 7 + 100], i,
                                      gui=gui, value=params[0 + 5 * i]),
                     ButtonIdentifier("Down", [i * consts.WINDOW_WIDTH / 4 + 200, 3 * consts.WINDOW_HEIGHT / 7 + 100],
                                      i, gui=gui, value=params[1 + 5 * i]),
                     ButtonIdentifier("Left", [i * consts.WINDOW_WIDTH / 4 + 200, 2 * consts.WINDOW_HEIGHT / 7 + 100],
                                      i, gui=gui, value=params[2 + 5 * i]),
                     ButtonIdentifier("Right", [i * consts.WINDOW_WIDTH / 4 + 200, 1 * consts.WINDOW_HEIGHT / 7 + 100],
                                      i, gui=gui, value=params[3 + 5 * i]),
                     ButtonIdentifier("Power-up",
                                      [i * consts.WINDOW_WIDTH / 4 + 200, 0 * consts.WINDOW_HEIGHT / 7 + 100], i,
                                      gui=gui, value=params[4 + 5 * i], is_button=True)]
                if i < len(Control.control.joysticks):
                    color = (255, 255, 255, 255)
                else:
                    color = (255, 0, 0, 255)
                gui.passive_elements += \
                    [pyglet.text.Label("Joystick %d" % i, x=i * consts.WINDOW_WIDTH / 4 + 200,
                                       y=5 * consts.WINDOW_HEIGHT / 7 + 100,
                                       anchor_x="center", anchor_y="center", color=color, font_size=40)]
        gui.focus = 0

    @staticmethod
    def get_name():
        return "config"


class GameSetup(SetupState):
    @staticmethod
    def setup(gui, params=None):
        gui.game_level = gui.active_elements[1].value
        gui.num_players = gui.active_elements[2].value
        gui.active_elements = []
        gui.passive_elements = []

    @staticmethod
    def get_name():
        return "game"
