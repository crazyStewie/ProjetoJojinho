from src.gui.Button import Button
from src.gui.Selector import Selector
from src.gui.ButtonIdentifier import ButtonIdentifier
from src.py_aux import consts
import pyglet
from src.utils import Control


class GUI:
    def __init__(self, window):
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.active_elements = []
        self.passive_elements = []
        self.config_params = None
        self.focus = -1
        self.window = window
        self.mode = ""

    def setup_initial_menu(self, params=None):
        self.mode = "initial"
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        if params is not None:
            self.active_elements = [Button("start", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 250])], gui=self),
                                    Selector("level", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 100])],
                                             value=params[0]),
                                    Selector("players", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -50])],
                                             value=params[1]),
                                    Button("settings", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -200])],
                                           gui=self),
                                    Button("quit", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -350])], self.window)]
        else:
            self.active_elements = [Button("start", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 250])], gui=self),
                                    Selector("level", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 100])]),
                                    Selector("players", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -50])]),
                                    Button("settings", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -200])],
                                           gui=self),
                                    Button("quit", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -350])], self.window)]

        self.passive_elements = \
            [pyglet.sprite.Sprite(pyglet.resource.image("background.png"))]
        self.focus = 0

    def setup_for_config_menu(self, params=None):
        self.mode = "config"
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        if params is None:
            self.active_elements = \
                [Button("return", [0*consts.WINDOW_WIDTH/4 + 200, 6*consts.WINDOW_HEIGHT/7 + 75], gui=self)]
            self.passive_elements = \
                [pyglet.sprite.Sprite(pyglet.resource.image("background.png"))]
            for i in range(4):
                self.active_elements += \
                    [ButtonIdentifier("Up", [i*consts.WINDOW_WIDTH/4 + 200, 4*consts.WINDOW_HEIGHT/7 + 100], i),
                     ButtonIdentifier("Down", [i*consts.WINDOW_WIDTH/4 + 200, 3*consts.WINDOW_HEIGHT/7 + 100], i),
                     ButtonIdentifier("Left", [i*consts.WINDOW_WIDTH/4 + 200, 2*consts.WINDOW_HEIGHT/7 + 100], i),
                     ButtonIdentifier("Right", [i*consts.WINDOW_WIDTH/4 + 200, 1*consts.WINDOW_HEIGHT/7 + 100], i),
                     ButtonIdentifier("Power-up", [i*consts.WINDOW_WIDTH/4 + 200, 0*consts.WINDOW_HEIGHT/7 + 100], i,
                                      is_button=True)]
                if i < len(Control.control.joysticks):
                    color = (255, 255, 255, 255)
                else:
                    color = (255, 0, 0, 255)
                self.passive_elements += \
                    [pyglet.text.Label("Joystick %d" % i, x=i*consts.WINDOW_WIDTH/4 + 200, y=5*consts.WINDOW_HEIGHT/7 + 100,
                                       anchor_x="center", anchor_y="center", color=color, font_size=40)]
        else:
            self.active_elements = \
                [Button("return", [0 * consts.WINDOW_WIDTH / 4 + 200, 6 * consts.WINDOW_HEIGHT / 7 + 75], gui=self)]
            self.passive_elements = \
                [pyglet.sprite.Sprite(pyglet.resource.image("background.png"))]
            for i in range(4):
                self.active_elements += \
                    [ButtonIdentifier("Up", [i * consts.WINDOW_WIDTH / 4 + 200, 4 * consts.WINDOW_HEIGHT / 7 + 100], i,
                                      value=params[0+5*i]),
                     ButtonIdentifier("Down", [i * consts.WINDOW_WIDTH / 4 + 200, 3 * consts.WINDOW_HEIGHT / 7 + 100],
                                      i, value=params[1+5*i]),
                     ButtonIdentifier("Left", [i * consts.WINDOW_WIDTH / 4 + 200, 2 * consts.WINDOW_HEIGHT / 7 + 100],
                                      i, value=params[2+5*i]),
                     ButtonIdentifier("Right", [i * consts.WINDOW_WIDTH / 4 + 200, 1 * consts.WINDOW_HEIGHT / 7 + 100],
                                      i, value=params[3+5*i]),
                     ButtonIdentifier("Power-up",
                                      [i * consts.WINDOW_WIDTH / 4 + 200, 0 * consts.WINDOW_HEIGHT / 7 + 100], i,
                                      value=params[4+5*i], is_button=True)]
                if i < len(Control.control.joysticks):
                    color = (255, 255, 255, 255)
                else:
                    color = (255, 0, 0, 255)
                self.passive_elements += \
                    [pyglet.text.Label("Joystick %d" % i, x=i * consts.WINDOW_WIDTH / 4 + 200,
                                       y=5 * consts.WINDOW_HEIGHT / 7 + 100,
                                       anchor_x="center", anchor_y="center", color=color, font_size=40)]
        self.focus = 0

    def setup_for_game(self):
        self.mode = "game"
        self.active_elements = []
        self.passive_elements = []

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
        elif Control.control.just_released("ui_down"):
            if self.focus < len(Control.control.joysticks)*5 or self.mode != "config":
                self.focus = min(len(self.active_elements) - 1, self.focus + 1)
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
