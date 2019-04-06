import pyglet


class Passerby:
    def __init__(self, sidewalk, relative_position, direction, pos, batch = None):
        self.sidewalk = sidewalk
        self.relative_position = relative_position
        self.direction = direction
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        image = pyglet.resource.image("Passerby.png")
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        if batch is not None:
            self.sprite = pyglet.sprite.Sprite(image, pos[0], pos[1], batch=batch)
        else:
            self.sprite = pyglet.sprite.Sprite(image, pos[0], pos[1])
