from src.game_elements.Map import Map
import pickle

game_map = Map()
game_map.crossings = [(300, 300),  (600, 300), (700, 150), (700, 450), (450, 450)]
game_map.streets = [(0, 1), (1, 2), (1, 3), (3, 4)]

with open("../../assets/levels/test_level.pickle", "wb") as f:
    pickle.dump(game_map, f, pickle.HIGHEST_PROTOCOL)
