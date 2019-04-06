import pyglet


class PowerUp:
    def __init__(self, type_, pos=(0, 0)):
        if type_ == 0:
            self.name = "accelerator"
            self.time_range = (5.0, 8.0)
        elif type_ == 1:
            self.name = "GPS"
            self.time_range = (3.0, 5.0)
        elif type_ == 2:
            self.name = "oil"
            self.time_range = (4.0, 7.0)
        elif type_ == 3:
            self.name = "invert"
            self.time_range = (7.0, 9.0)
        elif type_ == 4:
            self.name = "teleport"
            self.time_range = (4.5, 7.5)
        elif type_ == 5:
            self.name = "self_teleport"
            self.time_range = (3.5, 5.5)
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        image = pyglet.resource.image("%s.png" % self.name)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, pos[0], pos[1])
