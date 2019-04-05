from src.game_elements.Map import Map
from src.tools.map_creator.toolbar import Toolbar
from src.tools.map_creator import Editor
from src.tools.map_creator import Mouse
from src.tools.map_creator.ToolConsts import *
from src.utils import Control
import pickle
import pyglet
from pymunk.vec2d import Vec2d

map_creator_window = pyglet.window.Window(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, fullscreen=True)
Editor.editor.set_window(map_creator_window)
Control.control.setup(map_creator_window)
#with open("../../../assets/levels/test_level.pickle", "wb") as f:
#    pickle.dump(game_map, f, pickle.HIGHEST_PROTOCOL)


@map_creator_window.event
def on_mouse_press(x,y,button,modifier):
    button_id = 0
    if button == pyglet.window.mouse.RIGHT:
        button_id = 1
    if button == pyglet.window.mouse.MIDDLE:
        button_id = 2
    if not Mouse.mouse.is_pressed(button_id):
        Mouse.mouse.mouse_state[button_id] = Mouse.mouse.JUST_PRESSED


@map_creator_window.event
def on_mouse_release(x, y, button, modifier):
    button_id = 0
    if button == pyglet.window.mouse.RIGHT:
        button_id = 1
    if button == pyglet.window.mouse.MIDDLE:
        button_id = 2
    if Mouse.mouse.is_pressed(button_id):
        Mouse.mouse.mouse_state[button_id] = Mouse.mouse.JUST_RELEASED


@map_creator_window.event
def on_mouse_motion(x, y, dx ,dy):
    Mouse.mouse.position.x = x
    Mouse.mouse.position.y = y


@map_creator_window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    Mouse.mouse.position.x = x
    Mouse.mouse.position.y = y


def update(dt):
    Control.control.update(map_creator_window)
    Mouse.mouse.update(dt)
    Toolbar.toolbar.update(dt)
    Editor.editor.update(dt)
    pass


@map_creator_window.event
def on_draw():
    map_creator_window.clear()
    Editor.editor.draw()
    Toolbar.toolbar.draw()


pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
