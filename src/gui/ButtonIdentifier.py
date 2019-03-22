import pyglet
from src.utils import Control


class ButtonIdentifier:
    def __init__(self, label, pos, joystick, value=None, is_button=False):
        self.label = label
        if value is None:
            self.value = '-'
        else:
            self.value = value
        self.is_button = is_button
        self.x = pos[0]
        self.y = pos[1]
        self.joystick = joystick
        self.is_focused = False
        self.is_listening = False
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.text = pyglet.text.Label(self.label.capitalize(), x=self.x - 75, y=self.y,
                                      anchor_x="center", anchor_y="center", color=(0, 0, 0, 255), font_size=20)
        self.value_text = pyglet.text.Label(str(self.value), x=self.x + 50, y=self.y,
                                            anchor_x="center", anchor_y="center", color=(0, 0, 0, 255), font_size=20)
        default_image = pyglet.resource.image("button2_default.png")
        default_image.anchor_x = default_image.width // 2
        default_image.anchor_y = default_image.height // 2
        self.default_sprite = \
            pyglet.sprite.Sprite(default_image, pos[0], pos[1])
        pressed_image = pyglet.resource.image("button2_pressed.png")
        pressed_image.anchor_x = pressed_image.width // 2
        pressed_image.anchor_y = pressed_image.height // 2
        self.pressed_sprite = \
            pyglet.sprite.Sprite(pressed_image, pos[0], pos[1])
        self.pressed = 0
        self.sprites = [self.default_sprite, self.pressed_sprite]
        self.sprite = self.sprites[self.pressed]

    def update(self):
        if self.is_focused:
            if self.pressed:
                if self.joystick < len(Control.control.joysticks) and self.joystick != -1:
                    if self.is_button:
                        for button_id in range(len(Control.control.joysticks[self.joystick].buttons)):
                            if Control.control.joysticks[self.joystick].buttons[button_id]:
                                Control.control.set_joystick_input("%s%d" % (self.label, self.joystick),
                                                                   [(self.joystick, button_id)])
                                self.value = button_id
                                self.value_text.text = str(self.value)
                                self.pressed = 0
                    else:
                        for axis_id in range(len(Control.control.semi_axis[self.joystick])):
                            if Control.control.semi_axis[self.joystick][axis_id] > 0.5:
                                Control.control.set_semi_axis("%s%d" % (self.label, self.joystick),
                                                              (self.joystick, axis_id))
                                self.value = axis_id
                                self.value_text.text = str(self.value)
                                self.pressed = 0
                                break
            if Control.control.just_pressed("ui_action"):
                self.pressed = (self.pressed + 1) % 2
        else:
            self.pressed = 0
        self.sprite = self.sprites[self.pressed]

    def draw(self):
        self.sprite.draw()
        self.text.draw()
        self.value_text.draw()
