from src.utils.Control import Control
import time
import pyglet


class Selector:
    def __init__(self, pos, type):
        self.pos = pos
        self.is_focused = False
        self.type = type  # type should be "level" or "players"
        pyglet.resource.path = ["assets/sprites"]
        pyglet.resource.reindex()
        self.default_sprite = pyglet.sprite.Sprite(pyglet.resource.image('%s_selector_default.png' % type))
        self.default_sprite.update(pos[0], pos[1])
        self.pulsing_sprite = pyglet.sprite.Sprite(pyglet.resource.image('%s_selector_pulsing.png' % type))
        self.pulsing_sprite.update(pos[0], pos[1])
        self.sprite = self.default_sprite
        self.timer_begin = 0

    def update(self):
        if self.is_focused:
            if Control.just_pressed("ui_left"):
                self.timer_begin = time.perf_counter()
                self.sprite = self.pulsing_sprite
                self.decrement()
            if Control.just_pressed("ui_right"):
                self.timer_begin = time.perf_counter()
                self.sprite = self.pulsing_sprite
                self.increment()
            if time.perf_counter() - self.timer_begin >= 0.25:
                self.sprite = self.default_sprite
        else:
            self.sprite = self.default_sprite

        self.sprite.draw()

    def decrement(self):
        pass

    def increment(self):
        pass
