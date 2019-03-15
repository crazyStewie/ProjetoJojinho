import time
import pyglet
from src.utils import Control


class Selector:
    def __init__(self, pos, type_):
        self.pos = pos
        self.is_focused = False
        self.type = type_  # type should be "level" or "players"
        if self.type == "level":
            self.value = 1
        elif self.type == "players":
            self.value = 2
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.default_sprite = \
            pyglet.sprite.Sprite(pyglet.resource.image("%s_selector_default.png" % type), pos[0], pos[1])
        self.pulsing_sprite = \
            pyglet.sprite.Sprite(pyglet.resource.image("%s_selector_pulsing.png" % type), pos[0], pos[1])
        self.sprite = self.default_sprite
        self.timer_begin = 0

    def update(self):
        if self.is_focused:
            if Control.control.just_released("ui_left"):
                self.timer_begin = time.perf_counter()
                self.sprite = self.pulsing_sprite
                self.decrement()
            if Control.control.just_released("ui_right"):
                self.timer_begin = time.perf_counter()
                self.sprite = self.pulsing_sprite
                self.increment()
            if time.perf_counter() - self.timer_begin >= 0.25:
                self.sprite = self.default_sprite
        else:
            self.sprite = self.default_sprite

    def draw(self):
        self.sprite.draw()

    def decrement(self):
        if self.type == "level":
            self.value = max(1, self.value - 1)
        elif self.type == "players":
            self.value = max(2, self.value - 1)

    def increment(self):
        if self.type == "level":
            self.value = min(3, self.value + 1)
        elif self.type == "players":
            self.value = min(4, self.value + 1)
