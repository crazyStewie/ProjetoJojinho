from src.gui.GUI import GUI
from src.py_aux import consts
import pyglet

MAIN_MENU = 0
IN_GAME = 1
POST_GAME = 3


class Game:
    def __init__(self, window):
        self.current_state = MAIN_MENU
        self.window = window
        self.gui = GUI(self.window)
        self.gui.setup_initial_menu()
        pass

    def get_game_state(self):
        pass

    def update(self, dt):
        if self.gui.mode == "game":
            self.current_state = IN_GAME
        if self.current_state == MAIN_MENU:
            self.gui.update(dt)
        pass

    def draw(self):
        self.window.clear()
        if self.current_state == MAIN_MENU:
            self.gui.draw()
        pass
