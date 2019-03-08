from src.utils.Control import Control
import pyglet


class Button:
    def __init__(self, pos, type):
        self.pos = pos
        self.is_focused = False
        self.type = type  # type should be "start" or "config"
        pyglet.resource.path = ["assets/sprites"]
        pyglet.resource.reindex()
        self.default_sprite = pyglet.sprite.Sprite(pyglet.resource.image('%s_button_default.png' % type))
        self.default_sprite.update(pos[0], pos[1])
        self.pressed_sprite = pyglet.sprite.Sprite(pyglet.resource.image('%s_button_pressed.png' % type))
        self.pressed_sprite.update(pos[0], pos[1])
        self.sprite = self.default_sprite

    def update(self):
        if self.is_focused:
            if Control.is_pressed("ui_action"):
                self.sprite = self.pressed_sprite
        else:
            self.sprite = self.default_sprite

        if self.is_focused and Control.just_released("ui_action"):
            if self.type == "start":
                self.start_action()
            elif self.type == "config":
                self.config_action()

        self.sprite.draw()

    def start_action(self):
        pass

    def config_action(self):
        pass
