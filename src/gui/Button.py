import pyglet
from src.utils import Control


class Button:
    def __init__(self, type_, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.is_focused = False
        self.type = type_  # type should be "start", "settings" or "exit"
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.label = pyglet.text.Label(self.type.capitalize(), x=self.x, y=self.y, anchor_x="center", anchor_y="center",
                                       color=(0, 0, 0, 255))
        default_image = pyglet.resource.image("button_default.png")
        default_image.anchor_x = default_image.width//2
        default_image.anchor_y = default_image.height//2
        self.default_sprite = \
            pyglet.sprite.Sprite(default_image, pos[0], pos[1])
        pressed_image = pyglet.resource.image("button_pressed.png")
        pressed_image.anchor_x = pressed_image.width // 2
        pressed_image.anchor_y = pressed_image.height // 2
        self.pressed_sprite = \
            pyglet.sprite.Sprite(pressed_image, pos[0], pos[1])
        self.sprite = self.default_sprite

    def update(self):
        if self.is_focused:
            if Control.control.is_pressed("ui_action"):
                self.sprite = self.pressed_sprite
        else:
            self.sprite = self.default_sprite

        if self.is_focused and Control.control.just_released("ui_action"):
            if self.type == "start":
                self.start_action()
            elif self.type == "settings":
                self.config_action()

    def draw(self):
        self.sprite.draw()
        self.label.draw()

    def start_action(self):
        pass

    def config_action(self):
        pass
