import pyglet
import pymunk
import pymunk.pyglet_util

from src.utils import Control
from game_elements.Player import Player

main_window = pyglet.window.Window(width=960, height=600)
fps_display = pyglet.window.FPSDisplay(main_window)

space = pymunk.Space()
Control.control.setup(main_window)

player = Player(1, space)

options = pymunk.pyglet_util.DrawOptions()


bounding_body = pymunk.Body(1,body_type=pymunk.Body.STATIC)
bounding_segments = (pymunk.shapes.Segment(bounding_body,pymunk.vec2d.Vec2d(0,0),pymunk.vec2d.Vec2d(960,0),4),
                     pymunk.shapes.Segment(bounding_body,pymunk.vec2d.Vec2d(960,0),pymunk.vec2d.Vec2d(960,600),4),
                     pymunk.shapes.Segment(bounding_body,pymunk.vec2d.Vec2d(960,600),pymunk.vec2d.Vec2d(0,600),4),
                     pymunk.shapes.Segment(bounding_body,pymunk.vec2d.Vec2d(0, 600),pymunk.vec2d.Vec2d(0,0),4))
space.add(bounding_body, bounding_segments[0], bounding_segments[1],bounding_segments[2],bounding_segments[3])

def update(dt):
    Control.control.update(main_window)
    player.update(dt)
    space.step(dt)

@main_window.event
def on_draw():
    main_window.clear()
    fps_display.draw()
    player.draw()
    #space.debug_draw(options)

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
