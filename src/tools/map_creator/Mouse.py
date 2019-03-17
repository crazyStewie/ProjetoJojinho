from pymunk.vec2d import Vec2d


class Mouse:
    def __init__(self):
        self.PRESSED = 0
        self.RELEASED = 1
        self.JUST_PRESSED = 2
        self.JUST_RELEASED = 3
        self.position = Vec2d(0,0)
        self.mouse_state = [self.RELEASED, self.RELEASED, self.RELEASED]
        self.too_long = [False, False, False]
        self.button_count = 3

    def is_pressed(self, button):
        if self.mouse_state[button] == self.PRESSED or self.mouse_state[button] == self.JUST_PRESSED:
            return True
        return False

    def is_just_pressed(self, button):
        if self.mouse_state[button] == self.JUST_PRESSED:
            return True
        return False

    def is_just_released(self, button):
        if self.mouse_state[button] == self.JUST_RELEASED:
            return True
        return False

    def update(self, dt):
        for i in range(3):
            if self.mouse_state[i] == self.JUST_PRESSED:
                if self.too_long[i]:
                    self.mouse_state[i] = self.PRESSED
                    self.too_long[i] = False
                else:
                    self.too_long[i] = True
            elif self.mouse_state[i] == self.JUST_RELEASED:
                if self.too_long[i]:
                    self.mouse_state[i] = self.RELEASED
                    self.too_long[i] = False
                else:
                    self.too_long[i] = True


mouse = Mouse()
