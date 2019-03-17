import pyglet

from src.tools.map_creator.toolbar.ToolItem import ToolItem
from src.tools.map_creator import Mouse
from src.tools.map_creator import Editor

class __ToolBar:
    def __init__(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.button_size = 32
        pyglet.resource.path = ["../../../assets/sprites/tools"]
        pyglet.resource.reindex()
        print("initializing toolbar")

        self.button_images = [pyglet.resource.image("open_icon.png"),
                              pyglet.resource.image("save_icon.png"),
                              pyglet.resource.image("save_as_icon.png"),
                              pyglet.resource.image("add_icon.png"),
                              pyglet.resource.image("remove_icon.png"),
                              pyglet.resource.image("link_icon.png"),
                              pyglet.resource.image("unlink_icon.png"),
                              pyglet.resource.image("move_icon.png")]

        for img in self.button_images:
            img.anchor_x = img.width // 2
            img.anchor_y = img.height // 2

        selection_image = pyglet.resource.image("selected.png")
        selection_image.anchor_x = selection_image.width // 2
        selection_image.anchor_y = selection_image.height // 2
        self.selection_sprite = pyglet.sprite.Sprite(selection_image)

        hover_image = pyglet.resource.image("hover.png")
        hover_image.anchor_x = hover_image.width // 2
        hover_image.anchor_y = hover_image.height // 2
        self.hover_sprite = pyglet.sprite.Sprite(hover_image)

        self.button_types = ["open", "save", "save as", "add", "remove", "link", "unlink", "move"]
        self.button_count = len(self.button_types)

        self.selected = None
        self.last_selected = None
        self.buttons = []
        for i in range(self.button_count):
            self.buttons.append(ToolItem(pyglet.sprite.Sprite(self.button_images[i]), self.button_types[i], self.pos_x + self.button_size*(i-(self.button_count-1)/2), self.pos_y, self.button_size))
        self.size_x = self.button_size*self.button_count
        self.size_y = self.button_size
        self.is_hover = False

    def check_mouse_over(self):
        mouse_pos = Mouse.mouse.position
        if self.pos_x - self.size_x/2 < mouse_pos.x < self.pos_x + self.size_x/2:
            if self.pos_y - self.size_y / 2 < mouse_pos.y < self.pos_y + self.size_y / 2:
                self.is_hover = True
                return True
        self.is_hover = False
        return False

    def update(self, dt):
        self.check_mouse_over()
        # print("Selected = ", self.selected)
        # print("Last = ", self.last_selected)
        self.last_selected = self.selected
        for button in self.buttons:
            button.update(dt)
            if button.is_hover and Mouse.mouse.is_just_pressed(0):
                self.selected = button
        if self.selected:
            if self.selected.tool == "open":
                Editor.editor.open()
                self.selected = self.last_selected
            elif self.selected.tool == "save":
                Editor.editor.save()
                self.selected = self.last_selected
            elif self.selected.tool == "save as":
                Editor.editor.save_as()
                self.selected = self.last_selected
        pass

    def draw(self):
        for button in self.buttons:
            if button.is_hover:
                self.hover_sprite.position = button.sprite.position
                self.hover_sprite.draw()
            button.draw()
        if self.selected:
            self.selection_sprite.position = self.selected.sprite.position
            self.selection_sprite.draw()


toolbar = __ToolBar(480,16)
