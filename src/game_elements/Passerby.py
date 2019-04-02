import pyglet


class Passerby:
    def __init__(self, sidewalk, relative_position, direction, pos):
        self.sidewalk = sidewalk
        self.relative_position = relative_position
        self.direction = direction
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        image = pyglet.resource.image("Passerby.png")
        self.sprite = pyglet.sprite.Sprite(image, pos[0], pos[1])
