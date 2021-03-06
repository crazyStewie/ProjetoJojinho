import sys
print(sys.path[0])
parent_dir = sys.path[0][:len(sys.path[0])-4]
print(parent_dir)
sys.path += [parent_dir]

import pyglet
pyglet.options['debug_gl'] = False
import pymunk
import pymunk.pyglet_util
from src.utils.Game import Game
from src.utils import Control
from src.game_elements.Player import Player
from src.py_aux import consts
from src.gui.GUI import GUI

#fps_display = pyglet.window.FPSDisplay(main_window)
#gui = GUI(main_window)
#gui.setup_initial_menu()

#space = pymunk.Space()
#Control.control.setup(main_window)

#players = [Player(1, 100, 100, 0, space)]

#options = pymunk.pyglet_util.DrawOptions()


#bounding_body = pymunk.Body(1, body_type=pymunk.Body.STATIC)
#bounding_segments = \
#    (pymunk.shapes.Segment(bounding_body, pymunk.vec2d.Vec2d(0, 0), pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, 0), 4),
#     pymunk.shapes.Segment(bounding_body, pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, 0),
#                           pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT), 4),
#     pymunk.shapes.Segment(bounding_body, pymunk.vec2d.Vec2d(consts.WINDOW_WIDTH, consts.WINDOW_HEIGHT),
#                           pymunk.vec2d.Vec2d(0, consts.WINDOW_HEIGHT), 4),
#     pymunk.shapes.Segment(bounding_body, pymunk.vec2d.Vec2d(0, consts.WINDOW_HEIGHT), pymunk.vec2d.Vec2d(0, 0), 4))
#space.add(bounding_body, bounding_segments[0], bounding_segments[1], bounding_segments[2], bounding_segments[3])
#main_window = pyglet.window.Window(width=consts.WINDOW_WIDTH, height=consts.WINDOW_HEIGHT, fullscreen=True)
#game = Game(main_window)

#def update(dt):
#    Control.control.update(main_window)
#    game.update(dt)
    #gui.update()
#    for p in players:
#        p.update(dt)
    #space.step(dt)


#@main_window.event
#def on_draw():
#    game.draw()
    #main_window.clear()
    #fps_display.draw()
    #gui.draw()
#    for p in players:
#        p.draw()
    #space.debug_draw(options)


#pyglet.clock.schedule_interval(update, 1/consts.FPS)
game = Game()
pyglet.app.run()
