import pyglet
from src.game_elements.PowerUp import PowerUp

OUT_MARGIN = 8
HUD_WIDTH = 100 + 2 * OUT_MARGIN
HUD_HEIGHT = 80
POWER_UP_POSITION = (32, 32)
FUEL_BAR_POSITION = (71, 3)
MONEY_SYMBOL_WIDTH = 15
MONEY_LABEL_POSITION = (40, 73)


class HUD:
    def __init__(self, player, pos):
        self.player = player
        self.pos = pos
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        hud_layout_image = pyglet.resource.image('HUD_layout_%d.png' % self.player.player_id)
        self.hud_layout_sprite = pyglet.sprite.Sprite(hud_layout_image, pos[0], pos[1])
        fuel_bar_image = pyglet.resource.image('fuel_bar_temp.png')
        self.fuel_bar_sprite = pyglet.sprite.Sprite(fuel_bar_image, pos[0] + FUEL_BAR_POSITION[0],
                                                    pos[1] + FUEL_BAR_POSITION[1])
        self.value_label = pyglet.text.Label(text=self.fill_with_zeros(self.player.money, 5), x=pos[0] + MONEY_LABEL_POSITION[0],
                                             y=pos[1] + MONEY_LABEL_POSITION[1], anchor_x="center", anchor_y="center",
                                             color=(255, 255, 255, 255), font_size=12)

    @staticmethod
    def fill_with_zeros(number, length):
        string = str(number)
        while len(string) < length:
            string = "0" + string
        return string

    def update(self, dt):
        if self.player.power_up is not None:
            self.player.power_up.sprite.update(x=self.pos[0] + POWER_UP_POSITION[0],y=self.pos[1] + POWER_UP_POSITION[1])
        self.value_label.text = self.fill_with_zeros(self.player.money, 5)
        self.fuel_bar_sprite.scale_y = self.player.fuel

    def draw(self):
        if self.player.power_up is not None:
            self.player.power_up.sprite.draw()
        self.fuel_bar_sprite.draw()
        self.value_label.draw()
        self.hud_layout_sprite.draw()

