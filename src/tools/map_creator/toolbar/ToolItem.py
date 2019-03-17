import pyglet
from src.tools.map_creator import Mouse

class ToolItem:
    def __init__(self, sprite, tool, pos_x, pos_y, size):
        self.sprite = sprite
        self.tool = tool
        self.size = size
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.sprite.position = (pos_x, pos_y)
        self.label = pyglet.text.Label(tool,font_size=10, x=pos_x, y=pos_y + size/2, anchor_x="center",anchor_y="bottom")
        self.is_hover = False

    def check_mouse_over(self):
        mouse_pos = Mouse.mouse.position
        if self.pos_x - self.size/2 < mouse_pos.x < self.pos_x + self.size/2:
            if self.pos_y - self.size / 2 < mouse_pos.y < self.pos_y + self.size / 2:
                self.is_hover = True
                return True
        self.is_hover = False
        return False

    def update(self,dt):
        self.check_mouse_over()
        pass

    def draw(self):
        self.sprite.draw()
        if self.is_hover:
            self.label.draw()
