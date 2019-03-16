import time
import pyglet
from src.utils import Control


class Selector:
    def __init__(self, type_, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.is_focused = False
        self.type = type_  # type should be "level" or "players"
        if self.type == "level":
            self.value = 1
        elif self.type == "players":
            self.value = 2
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.label = pyglet.text.Label(text=self.type.capitalize(),
                                       x=self.x, y=self.y+30, anchor_x="center", anchor_y="center",
                                       color=(0, 0, 0, 255))
        self.value_label = pyglet.text.Label(text=str(self.value),
                                             x=self.x, y=self.y, anchor_x="center", anchor_y="center",
                                             color=(0, 0, 0, 255))
        default_image = pyglet.resource.image("selector_default.png")
        default_image.anchor_x = default_image.width // 2
        default_image.anchor_y = default_image.height // 2
        self.default_sprite = \
            pyglet.sprite.Sprite(default_image, pos[0], pos[1])
        pulsing_image = pyglet.resource.image("selector_pulsing.png")
        pulsing_image.anchor_x = pulsing_image.width // 2
        pulsing_image.anchor_y = pulsing_image.height // 2
        self.pulsing_sprite = \
            pyglet.sprite.Sprite(pulsing_image, pos[0], pos[1])
        self.sprite = self.default_sprite
        self.timer_begin = 0

    def update(self):
        if self.is_focused:
            if Control.control.just_released("ui_left"):
                self.timer_begin = time.perf_counter()
                self.sprite = self.pulsing_sprite
                self.decrement()
                self.value_label.text = str(self.value)
            if Control.control.just_released("ui_right"):
                self.timer_begin = time.perf_counter()
                self.sprite = self.pulsing_sprite
                self.increment()
                self.value_label.text = str(self.value)
            if time.perf_counter() - self.timer_begin >= 0.15:
                self.sprite = self.default_sprite
        else:
            self.sprite = self.default_sprite

    def draw(self):
        self.sprite.draw()
        self.label.draw()
        self.value_label.draw()

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
