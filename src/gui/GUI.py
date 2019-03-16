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

    @staticmethod
    def draw_box(corner1, corner2):
        pyglet.graphics.draw(5, pyglet.gl.GL_LINE_STRIP, ("v2f", (corner1[0], corner1[1],
                                                                  corner2[0], corner1[1],
                                                                  corner2[0], corner2[1],
                                                                  corner1[0], corner2[1],
                                                                  corner1[0], corner1[1])))

    def update(self):
        if Control.control.just_released("ui_up"):
            self.focus = max(0, self.focus - 1)
        elif Control.control.just_released("ui_down"):
            self.focus = min(4, self.focus + 1)
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

        corner1 = (self.active_elements[self.focus].x -
                   self.active_elements[self.focus].default_sprite.width//2 - consts.BOX_MARGIN,
                        self.active_elements[self.focus].y -
                    self.active_elements[self.focus].default_sprite.height // 2 - consts.BOX_MARGIN)
        corner2 = (self.active_elements[self.focus].x +
                   self.active_elements[self.focus].default_sprite.width // 2 + consts.BOX_MARGIN,
                   self.active_elements[self.focus].y +
                   self.active_elements[self.focus].default_sprite.height // 2 + consts.BOX_MARGIN)
        self.draw_box(corner1, corner2)
