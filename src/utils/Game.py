class Game:
    MAIN_MENU = 0
    IN_GAME = 1
    POST_GAME = 3

    def __init__(self):
        self.current_state = self.MAIN_MENU
        pass

    def get_player_count(self):
        pass

    def get_player_fuel(self, player_id):
        pass

    def get_player_score(self, player_id):
        pass

    def get_game_state(self):
        pass

    def update(self, dt):
        pass

    def draw(self, dt):
        pass


game_state = Game()
