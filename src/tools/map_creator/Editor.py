from src.game_elements.Map import Map
import pyglet
import pickle
import copy
import tkinter.filedialog
from pymunk.vec2d import Vec2d
from src.tools.map_creator.toolbar import Toolbar
from src.tools.map_creator import Mouse
from src.tools.map_creator.ToolConsts import *



class __Editor:
    def __init__(self):
        tkinter.Tk().withdraw()
        self.map = Map()
        self.circles = []
        self.is_hover = None
        self.hover_indicator = None
        self.is_linking = None
        self.is_unlinking = None
        self.link_indicator = None
        self.is_moving = None
        self.move_last = (0,0)
        self.streets = []
        self.filepath = None
        self.grid = None
        self.grid_size = 120
        self.grid_start = Vec2d(self.grid_size/2, self.grid_size/2)
        self.make_grid()
        self.grid_enabled = True

    def get_grid_mouse(self):
        if self.grid_enabled:
            return Vec2d(Mouse.mouse.position.x - (Mouse.mouse.position.x) % self.grid_size + self.grid_size/2,
                         Mouse.mouse.position.y - (Mouse.mouse.position.y) % self.grid_size + self.grid_size/2)
        return Mouse.mouse.position

    def make_grid(self):
        verts = []
        color = []
        x = self.grid_size/2
        while x < WINDOW_WIDTH:
            verts += [x, 0,
                                x, WINDOW_HEIGHT]
            color += [255, 255, 255, 100, 255, 255, 255, 100]
            x += self.grid_size
        y = self.grid_size/2
        while y < WINDOW_HEIGHT:
            verts += [0, y,
                                 WINDOW_WIDTH, y]
            color += [255, 255, 255, 100, 255, 255, 255, 100]
            y += self.grid_size
        self.grid = pyglet.graphics.vertex_list(len(verts)//2, ("v2f", verts), ("c4B", color))

        pass

    def draw_grid(self):
        if self.grid is None:
            return
        self.grid.draw(pyglet.gl.GL_LINES)

        pass

    def make_circle(self, pos_x, pos_y,radius):
        resolution = 32
        verts = []
        radius = Vec2d(radius, 0)
        for i in range(resolution):
            verts += [radius.x + pos_x, radius.y + pos_y]
            radius.rotate_degrees(360/resolution)
        return verts
        #return pyglet.graphics.vertex_list(resolution, ('v2f', verts))

    def update_draw_map(self):
        for street in self.streets:
            street.delete()
        self.streets = []
        for street in self.map.streets:
            begin = Vec2d(self.map.crossings[street[0]])
            end = Vec2d(self.map.crossings[street[1]])
            normal = (end - begin).rotated_degrees(90).normalized()
            corner1 = begin + self.map.STREET_WIDTH / 2 * normal
            corner2 = end + self.map.STREET_WIDTH / 2 * normal
            corner3 = end + self.map.STREET_WIDTH / 2 * (-normal)
            corner4 = begin + self.map.STREET_WIDTH / 2 * (-normal)
            self.streets.append(pyglet.graphics.vertex_list(4, ("v2f", (corner1.x, corner1.y,
                                                                        corner2.x, corner2.y,
                                                                        corner3.x, corner3.y,
                                                                        corner4.x, corner4.y)),
                                                            ("c3B", (128, 128, 128)*4)))
        for circle in self.circles:
            circle.delete()
        self.circles = []
        for cross in self.map.crossings:
            x,y = cross
            self.circles.append(pyglet.graphics.vertex_list(32, ("v2f", self.make_circle(x,y,self.map.STREET_WIDTH/2))))
        pass

    def draw_map(self):
        for street in self.streets:
            street.draw(pyglet.gl.GL_QUADS)
        for circle in self.circles:
            circle.draw(pyglet.gl.GL_POLYGON)

    def check_mouse_over(self):
        self.is_hover = None
        for i in range(len(self.map.crossings)):
            if Mouse.mouse.position.get_distance(Vec2d(self.map.crossings[i])) < self.map.STREET_WIDTH/2:
                self.is_hover = i

    def update_hover_indicator(self):
        if self.hover_indicator:
            self.hover_indicator.delete()
        if self.is_hover is None and self.hover_indicator:
            self.hover_indicator = None
        if self.is_hover is not None:
            x, y = self.map.crossings[self.is_hover]
            self.hover_indicator = pyglet.graphics.vertex_list(32, ("v2f", self.make_circle(x, y, 0.6 * self.map.STREET_WIDTH)), ("c3B", (125, 175, 255)*32))

    def update_link_indicator(self):
        resolution = 32
        begin = None
        end = None
        if self.link_indicator:
            self.link_indicator.delete()
        if self.is_linking is None and self.is_unlinking is None and self.link_indicator:
            self.link_indicator = None
        if self.is_linking is not None or self.is_unlinking is not None:
            if self.is_unlinking is not None:
                begin = self.is_unlinking
            else:
                begin = self.is_linking
            end = Mouse.mouse.position
            if self.is_hover is not None:
                if begin != self.is_hover:
                    end = Vec2d(self.map.crossings[self.is_hover])

            begin = Vec2d(self.map.crossings[begin])
            direction = (end-begin)
            angle = direction.angle
            vectors = []
            radius = Vec2d(0,0.8*self.map.STREET_WIDTH)
            vectors.append(radius.rotated(angle))
            for i in range(resolution//2):
                radius.rotate_degrees(360/resolution)
                vectors.append(radius.rotated(angle))
            vectors.append(radius.rotated(angle) + direction)
            for i in range(resolution//2):
                radius.rotate_degrees(360/resolution)
                vectors.append(radius.rotated(angle) + direction)
            verts = []
            for vector in vectors:
                verts += [vector.x + begin.x, vector.y+begin.y]
            if self.is_linking is not None:
                self.link_indicator = pyglet.graphics.vertex_list(resolution+2, ('v2f', verts), ("c3B", (50,200,100)*(resolution+2)))
            else:
                self.link_indicator = pyglet.graphics.vertex_list(resolution + 2, ('v2f', verts),
                                                                  ("c3B", (220, 60, 30) * (resolution + 2)))

    def update(self, dt):
        self.check_mouse_over()

        if self.is_moving is not None:
            self.map.crossings[self.is_moving] = (self.get_grid_mouse().x, self.get_grid_mouse().y)
            if Mouse.mouse.is_just_released(0):
                is_move_valid = True
                if Toolbar.toolbar.is_hover or not (0 < self.get_grid_mouse().x < WINDOW_WIDTH and 0 < self.get_grid_mouse().y < WINDOW_HEIGHT):
                    print("invalid move, invalid cursor position at ", Mouse.mouse.position.x, ", ", Mouse.mouse.position.y)
                    is_move_valid = False
                for i in range(len(self.map.crossings)):
                    if i != self.is_moving:
                        cross_pos = Vec2d(self.map.crossings[i])
                        if cross_pos.get_distance(self.get_grid_mouse()) < self.map.STREET_WIDTH:
                            print("invalid move")
                            is_move_valid = False
                if not is_move_valid:
                    self.map.crossings[self.is_moving] = self.move_last
                self.is_moving = None

        if self.is_linking is not None:
            if Mouse.mouse.is_just_pressed(0):
                to_link = self.is_hover
                is_link_valid = (to_link is not None and to_link != self.is_linking)
                for street in self.map.streets:
                    if to_link in street and self.is_linking in street:
                        is_link_valid = False
                if is_link_valid:
                    self.map.streets += [(self.is_linking, to_link)]
                self.is_linking = None

        if self.is_unlinking is not None:
            if Mouse.mouse.is_just_pressed(0):
                to_unlink = self.is_hover
                is_unlink_valid = (to_unlink is not None and to_unlink != self.is_unlinking)
                for street in self.map.streets:
                    if is_unlink_valid and to_unlink in street and self.is_unlinking in street:
                        self.map.streets.remove(street)
                self.is_unlinking = None

        if not Toolbar.toolbar.is_hover:
            if Toolbar.toolbar.selected:
                if Toolbar.toolbar.selected.tool == "add":
                    self.is_moving = None
                    self.is_linking = None
                    self.is_unlinking = None
                    if Mouse.mouse.is_just_pressed(0):
                        is_add_valid = True
                        for cross in self.map.crossings:
                            cross_pos = Vec2d(cross)
                            if cross_pos.get_distance(self.get_grid_mouse()) < self.map.STREET_WIDTH:
                                is_add_valid = False
                        if is_add_valid:
                            self.map.crossings.append((self.get_grid_mouse().x, self.get_grid_mouse().y))
                if Toolbar.toolbar.selected.tool == "remove":
                    self.is_moving = None
                    self.is_linking = None
                    self.is_unlinking = None
                    if Mouse.mouse.is_just_pressed(0):
                        if self.is_hover is not None:
                            to_remove =[]
                            for i in range(len(self.map.streets)):
                                if self.is_hover in self.map.streets[i]:
                                    to_remove.append(self.map.streets[i])
                                else:
                                    ca, cb = self.map.streets[i]
                                    if ca > self.is_hover:
                                        ca -= 1
                                    if cb > self.is_hover:
                                        cb -= 1
                                    self.map.streets[i] = (ca, cb)
                            for street in to_remove:
                                self.map.streets.remove(street)
                            self.map.crossings.pop(self.is_hover)
                            self.is_hover = None
                if Toolbar.toolbar.selected.tool == "move":
                    if self.is_moving is None:
                        if self.is_hover is not None and Mouse.mouse.is_just_pressed(0):
                            self.is_moving = self.is_hover
                            self.move_last = self.map.crossings[self.is_moving]
                if Toolbar.toolbar.selected.tool == "link":
                    if self.is_linking is None:
                        if self.is_hover is not None and Mouse.mouse.is_just_pressed(0):
                            self.is_linking = self.is_hover
                if Toolbar.toolbar.selected.tool == "unlink":
                    if self.is_unlinking is None:
                        if self.is_hover is not None and Mouse.mouse.is_just_pressed(0):
                            self.is_unlinking = self.is_hover

        self.update_hover_indicator()
        self.update_draw_map()
        self.update_link_indicator()
        pass

    def draw(self):
        self.draw_map()
        if self.hover_indicator:
            self.hover_indicator.draw(pyglet.gl.GL_LINE_LOOP)
        if self.link_indicator:
            self.link_indicator.draw(pyglet.gl.GL_LINE_LOOP)
        self.draw_grid()

    def open(self):
        print("opening a file")
        self.filepath = tkinter.filedialog.askopenfilename()
        print(self.filepath)
        if self.filepath.endswith(".pickle"):
            with open(self.filepath, "rb") as f:
                self.map = pickle.load(f)

    def save(self):
        if self.filepath is None or self.filepath == "":
            self.filepath = tkinter.filedialog.asksaveasfilename(defaultextension=".pickle")
        if self.filepath != "":
            with open (self.filepath, "wb") as f:
                pickle.dump(self.map, f, pickle.HIGHEST_PROTOCOL)
        pass

    def save_as(self):
        self.filepath = tkinter.filedialog.asksaveasfilename(defaultextension=".pickle")
        if self.filepath != "":
            with open (self.filepath, "wb") as f:
                pickle.dump(self.map, f, pickle.HIGHEST_PROTOCOL)
        pass


editor = __Editor()
