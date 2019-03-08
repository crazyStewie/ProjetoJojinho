class GUI:
    def __init__(self):
        self.active_elements = []
        self.passive_elements = []

    def setup_initial_menu(self):
        self.active_elements = []
        self.passive_elements = []

    def setup_for_game(self):
        self.active_elements = []
        self.passive_elements = []

    def update(self):
        for elem in self.active_elements:
            elem.update()

