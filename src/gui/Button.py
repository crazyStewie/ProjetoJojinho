import pyglet
from src.utils import Control


class Button:
    def __init__(self, type_, pos, gui, window=None):
        self.x = pos[0]
        self.y = pos[1]
        if window is None and type == "quit":
            raise Exception("The window should be passed as an argument to the constructor in this case!")
        if gui is None and (type == "config" or type == "return"):
            raise Exception("The gui should be passed as an argument to the constructor in this case!")
        self.window = window
        self.gui = gui
        self.is_focused = False
        self.type = type_  # type should be "start", "settings" or "exit"
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        self.label = pyglet.text.Label(self.type.capitalize(), x=self.x, y=self.y, anchor_x="center", anchor_y="center",
                                       color=(0, 0, 0, 255), font_size=20)
        default_image = pyglet.resource.image("button_default.png")
        default_image.anchor_x = default_image.width//2
        default_image.anchor_y = default_image.height//2
        self.default_sprite = \
            pyglet.sprite.Sprite(default_image, pos[0], pos[1])
        pressed_image = pyglet.resource.image("button_pressed.png")
        pressed_image.anchor_x = pressed_image.width//2
        pressed_image.anchor_y = pressed_image.height//2
        self.pressed_sprite = \
            pyglet.sprite.Sprite(pressed_image, pos[0], pos[1])
        if self.type == "return":
            self.default_sprite.scale_x = 0.5
            self.default_sprite.scale_y = 0.7
            self.pressed_sprite.scale_x = 0.5
            self.pressed_sprite.scale_y = 0.7
        self.sprite = self.default_sprite

    def update(self, dt):
        if self.is_focused:
            if Control.control.is_pressed("ui_action"):
                self.sprite = self.pressed_sprite
            else:
                self.sprite = self.default_sprite
        else:
            self.sprite = self.default_sprite

        if self.is_focused and Control.control.just_released("ui_action"):
            self.gui.play_sound = True
            self.gui.sound = "select"
            if self.type == "start":
                self.start_action()
            elif self.type == "settings":
                self.config_action()
            elif self.type == "return":
                self.return_action()
            elif self.type == "quit":
                self.quit_action()

    def draw(self):
        self.sprite.draw()
        self.label.draw()

    def start_action(self):
        self.gui.setup_for_game()

    def config_action(self):
        config_params = []
        for i in range(len(self.gui.active_elements)):
            if i == 1 or i == 2:
                config_params += [self.gui.active_elements[i].value]
        self.gui.setup_for_config_menu(self.gui.config_params)
        self.gui.config_params = config_params

    def return_action(self):
        config_params = []
        for i in range(len(self.gui.active_elements)):
            if i > 0:
                config_params += [self.gui.active_elements[i].value]
        self.gui.setup_initial_menu(self.gui.config_params)
        self.gui.config_params = config_params

    def quit_action(self):
        self.window.close()
