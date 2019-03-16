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
        button_box_image = pyglet.resource.image("button_box.png")
        button_box_image.anchor_x = button_box_image.width // 2
        button_box_image.anchor_y = button_box_image.height // 2
        selector_box_image = pyglet.resource.image("selector_box.png")
        selector_box_image.anchor_x = selector_box_image.width // 2
        selector_box_image.anchor_y = selector_box_image.height // 2
        self.button_box = pyglet.sprite.Sprite(button_box_image)
        self.selector_box = pyglet.sprite.Sprite(selector_box_image)
        self.focus = -1

    def setup_initial_menu(self):
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.active_elements = [Button("start", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 150])]),
                                Selector("level", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, 50])]),
                                Selector("players", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -50])]),
                                Button("settings", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -150])]),
                                Button("quit", [sum(x) for x in zip(consts.WINDOW_CENTER, [0, -250])])]

        self.passive_elements = \
            [pyglet.sprite.Sprite(pyglet.resource.image("background.png"))]
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
        if type(self.active_elements[self.focus]) is Button:
            self.button_box.x = self.active_elements[self.focus].x
            self.button_box.y = self.active_elements[self.focus].y
        elif type(self.active_elements[self.focus]) is Selector:
            self.selector_box.x = self.active_elements[self.focus].x
            self.selector_box.y = self.active_elements[self.focus].y

        for index, elem in enumerate(self.active_elements):
            if index == self.focus:
                elem.is_focused = True
            else:
                elem.is_focused = False
            elem.update()

    def draw(self):
        for elem in self.passive_elements:
            elem.draw()
        for elem in self.active_elements:
            elem.draw()
        if type(self.active_elements[self.focus]) is Button:
            self.button_box.draw()
        elif type(self.active_elements[self.focus]) is Selector:
            self.selector_box.draw()
