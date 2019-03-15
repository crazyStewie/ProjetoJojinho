from src.gui.Button import Button
from src.gui.Selector import Selector
from src.py_aux import consts
import pyglet
from src.utils import Control


class GUI:
    def __init__(self):
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.active_elements = []
        self.passive_elements = []
        self.box = pyglet.sprite.Sprite(pyglet.resource.image("box.png"))
        self.focus = -1

    def setup_initial_menu(self):
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.active_elements = [Button("start", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 50])]),
                                Selector("level", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 0])]),
                                Selector("players", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -50])]),
                                Button("config", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -100])]),
                                Button("quit", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -150])])]
        self.passive_elements = \
            [pyglet.sprite.Sprite(pyglet.resource.image("background.png"), consts.WINDOW_CENTER)]
        self.focus = 0

    def setup_for_config_menu(self):
        self.active_elements = []
        self.passive_elements = []

    def setup_for_game(self):
        self.active_elements = []
        self.passive_elements = []

    def update(self):
        if Control.control.just_released("ui_up"):
            self.focus = max(0, self.focus - 1)
        elif Control.control.just_released("ui_down"):
            self.focus = min(4, self.focus + 1)
        self.box.x = self.active_elements[self.focus].x
        self.box.y = self.active_elements[self.focus].y
        for index, elem in enumerate(self.active_elements):
            if index == self.focus:
                elem.is_focused = True
            else:
                elem.is_focused = False
            elem.update()

    def draw(self):
        for elem in self.active_elements:
            elem.draw()
        for elem in self.passive_elements:
            elem.draw()
        self.box.draw()
