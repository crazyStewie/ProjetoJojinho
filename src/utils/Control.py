import pyglet.window
from pyglet.window import key


class Control:
    def __init__(self, window):
        self.actions = {}
        self.action_state = {}

        self.keys = key.KeyStateHandler()
        window.push_handlers(self.keys)

        self.PRESSED = 0
        self.RELEASED = 1
        self.JUST_PRESSED = 2
        self.JUST_RELEASED = 3

        self.add_input("ui_up", [key.UP])
        self.add_input("ui_down", [key.DOWN])
        self.add_input("ui_left", [key.LEFT])
        self.add_input("ui_right", [key.RIGHT])
        self.add_input("ui_action", [key.ENTER])
        pass

    def is_pressed(self, action):
        if self.action_state[action] == self.PRESSED or self.action_state[action] == self.JUST_PRESSED:
            return True
        return False

    def just_pressed(self, action):
        if self.action_state[action] == self.JUST_PRESSED:
            return True
        return False

    def just_released(self, action):
        if self.action_state[action] == self.JUST_RELEASED:
            return True
        return False

    def add_input(self, action, inputs):
        self.actions[action] = inputs
        self.action_state[action] = self.RELEASED
        pass

    def update(self, window):
        window.push_handlers(self.keys)
        for key, event in self.keys.items():
            for action, input in self.actions.items():
                if key in input:
                    last = self.action_state[action]
                    if event == 1:
                        if last == self.RELEASED or last == self.JUST_RELEASED:
                            current = self.JUST_PRESSED
                        else:
                            current = self.PRESSED
                    else:
                        if last == self.PRESSED or last == self.JUST_PRESSED:
                            current = self.JUST_RELEASED
                        else:
                            current = self.RELEASED
                    self.action_state[action] = current
