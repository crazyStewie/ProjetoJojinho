import pyglet
from pyglet.window import key
def numcap(num,min,max):
    if num < min:
        return min
    if num > max:
        return max
    return num

class Control:
    def __init__(self):
        self.joysticks = pyglet.input.get_joysticks()
        for joystick in self.joysticks:
            joystick.open()
        print(len(self.joysticks)," joysticks were found")
        self.actions = {}
        self.joystick_actions= {}
        self.axis_actions = {}
        self.action_state = {}
        self.keys = key.KeyStateHandler()
        self.PRESSED = 0
        self.RELEASED = 1
        self.JUST_PRESSED = 2
        self.JUST_RELEASED = 3
        self.set_input("ui_up", [key.UP])
        self.set_input("ui_down", [key.DOWN])
        self.set_input("ui_left", [key.LEFT])
        self.set_input("ui_right", [key.RIGHT])
        self.set_input("ui_action", [key.ENTER])
        self.set_semi_axis("Up0", (0, 5))
        self.set_semi_axis("Down0", (0, 4))
        self.set_semi_axis("Left0", (0, 1))
        self.set_semi_axis("Right0", (0, 0))
        self.set_semi_axis("Up1", (1, 5))
        self.set_semi_axis("Down1", (1, 4))
        self.set_semi_axis("Left1", (1, 1))
        self.set_semi_axis("Right1", (1, 0))
        self.set_semi_axis("Up2", (2, 5))
        self.set_semi_axis("Down2", (2, 4))
        self.set_semi_axis("Left2", (2, 1))
        self.set_semi_axis("Right2", (2, 0))
        self.set_semi_axis("Up3", (3, 5))
        self.set_semi_axis("Down3", (3, 4))
        self.set_semi_axis("Left3", (3, 1))
        self.set_semi_axis("Right3", (3, 0))
        self.semi_axis = []
        for i in range(len(self.joysticks)):
            self.semi_axis += [(numcap(self.joysticks[i].x, 0, 1), -numcap(self.joysticks[i].x, -1, 0),
                                numcap(self.joysticks[i].rx, 0, 1), -numcap(self.joysticks[i].rx, -1, 0),
                                numcap(self.joysticks[i].y, 0, 1), -numcap(self.joysticks[i].y, -1, 0),
                                numcap(self.joysticks[i].ry, 0, 1), -numcap(self.joysticks[i].ry, -1, 0),
                                numcap(self.joysticks[i].z, 0, 1), -numcap(self.joysticks[i].z, -1, 0),
                                numcap(self.joysticks[i].rz, 0, 1), -numcap(self.joysticks[i].rz, -1, 0),
                                numcap(self.joysticks[i].hat_x, 0, 1), -numcap(self.joysticks[i].hat_x, -1, 0),
                                numcap(self.joysticks[i].hat_y, 0, 1), -numcap(self.joysticks[i].hat_y, -1, 0))]

    def setup(self, window):
        window.push_handlers(self.keys)

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

    def set_input(self, action, inputs):
        self.actions[action] = inputs
        self.action_state[action] = self.RELEASED
        pass

    def set_joystick_input(self, action, inputs):
        self.joystick_actions[action] = inputs
        self.action_state[action] = self.RELEASED

    def set_semi_axis(self, action, axis):
        self.axis_actions[action] = axis

    def get_axis(self, action):
        joy_id, axis_id = self.axis_actions[action]
        if joy_id < len(self.semi_axis):
            this_joy = self.semi_axis[joy_id]
            return this_joy[axis_id]
        return 0

    def update(self, window):
        for i in range(len(self.joysticks)):
            self.semi_axis[i] = (numcap(self.joysticks[i].x, 0, 1), -numcap(self.joysticks[i].x, -1, 0),
                                numcap(self.joysticks[i].rx, 0, 1), -numcap(self.joysticks[i].rx, -1, 0),
                                numcap(self.joysticks[i].y, 0, 1), -numcap(self.joysticks[i].y, -1, 0),
                                numcap(self.joysticks[i].ry, 0, 1), -numcap(self.joysticks[i].ry, -1, 0),
                                numcap(self.joysticks[i].z, 0, 1), -numcap(self.joysticks[i].z, -1, 0),
                                numcap(self.joysticks[i].rz, 0, 1), -numcap(self.joysticks[i].rz, -1, 0),
                                numcap(self.joysticks[i].hat_x, 0, 1), -numcap(self.joysticks[i].hat_x, -1, 0),
                                numcap(self.joysticks[i].hat_y, 0, 1), -numcap(self.joysticks[i].hat_y, -1, 0))
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
        for joy in range(len(self.joysticks)):
            for action, input in self.joystick_actions.items():
                for (joy_id, key_id) in input:
                    if joy == joy_id:
                        last = self.action_state[action]
                        if self.joysticks[joy].buttons[key_id]:
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


control = Control()
