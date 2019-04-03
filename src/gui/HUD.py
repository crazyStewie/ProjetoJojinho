import pyglet

OUT_MARGIN = 8
HUD_WIDTH = 100 + 2 * OUT_MARGIN
HUD_HEIGHT = 80
POWER_UP_POSITION = (32, 32)
FUEL_BAR_POSITION = (71, 3)
MONEY_SYMBOL_WIDTH = 15
MONEY_LABEL_POSITION = (25, 73)


class HUD:
    def __init__(self, player, pos):
        self.player = player
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        hud_layout_image = pyglet.resource.image('HUD_layout_%d.png' % self.player.player_id)
        self.hud_layout_sprite = pyglet.sprite.Sprite(hud_layout_image, pos[0], pos[1])
        power_up_image = pyglet.resource.image('power_up_temp.png')
        power_up_image.anchor_x = power_up_image.width // 2
        power_up_image.anchor_y = power_up_image.height // 2
        self.power_up_sprite = pyglet.sprite.Sprite(power_up_image, pos[0] + POWER_UP_POSITION[0],
                                                    pos[1] + POWER_UP_POSITION[1])
        fuel_bar_image = pyglet.resource.image('fuel_bar_temp.png')
        self.fuel_bar_sprite = pyglet.sprite.Sprite(fuel_bar_image, pos[0] + FUEL_BAR_POSITION[0],
                                                    pos[1] + FUEL_BAR_POSITION[1])
        self.value_label = pyglet.text.Label(text=str(self.player.money), x=pos[0] + MONEY_LABEL_POSITION[0],
                                             y=pos[1] + MONEY_LABEL_POSITION[1], anchor_x="center", anchor_y="center",
                                             color=(255, 255, 255, 255), font_size=12)

    def update(self, dt):
        self.fuel_bar_sprite.scale_y = self.player.fuel

    def draw(self):
        self.power_up_sprite.draw()
        self.fuel_bar_sprite.draw()
        self.value_label.draw()
        self.hud_layout_sprite.draw()

