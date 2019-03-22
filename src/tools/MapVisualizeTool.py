import pyglet
import pickle
from pymunk.vec2d import Vec2d

window = pyglet.window.Window(width=960, height=600)
with open("../../assets/levels/test_level.pickle", "rb") as f:
    game_map = pickle.load(f)


def draw_street(map_, street):
    begin = Vec2d(map_.crossings[street[0]])
    end = Vec2d(map_.crossings[street[1]])
    normal = (end - begin).rotated_degrees(90).normalized()
    corner1 = begin + map_.STREET_WIDTH / 2 * normal
    corner2 = end + map_.STREET_WIDTH / 2 * normal
    corner3 = end + map_.STREET_WIDTH / 2 * (-normal)
    corner4 = begin + map_.STREET_WIDTH / 2 * (-normal)
    print(corner1, corner2, corner3, corner4)
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ("v2f", (corner1.x, corner1.y,
                                                         corner2.x, corner2.y,
                                                         corner3.x, corner3.y,
                                                         corner4.x, corner4.y)))


@window.event
def on_draw():
    window.clear()
    for street in game_map.streets:
        draw_street(game_map, street)


pyglet.app.run()
