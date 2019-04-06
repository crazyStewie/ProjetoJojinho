import pyglet
from src.py_aux import consts


class EndScreen:
    def __init__(self, total_scores = [1750,1500,1420,1600]):
        num_players = len(total_scores)
        self.background_graphics = []
        self.background_elements = []
        self.colors = [(250, 230, 60), (20, 240, 90), (240, 90, 90), (40, 110, 240)]
        self.stacks = pyglet.graphics.Batch()
        self.stack_sprites = []
        self.money_amount = [0]*num_players
        self.total_scores = total_scores
        self.num_players = num_players
        self.money_labels = []
        self.setup_background()

        pyglet.resource.path = ["../assets/sprites"]
        self.money_image = pyglet.resource.image("end_screen/money_icon.png")
        self.money_image.anchor_x = self.money_image.width // 2
        self.money_image.anchor_y = self.money_image.height // 2
        self.stack_tops = [200]*num_players
        self.stack_sizes = [0]*num_players
        self.ANIMATION_SCALE = 250


    def setup_background(self):
        step = 260
        for i in range(self.num_players):
            center_x = consts.WINDOW_WIDTH/2 - self.num_players/2*(step+15) + (i+0.5)*(step+15)
            verts = [center_x-step/2, 0,
                     center_x+step/2, 0,
                     center_x+step/2, consts.WINDOW_HEIGHT,
                     center_x-step/2, consts.WINDOW_HEIGHT]
            self.background_graphics += [pyglet.graphics.vertex_list(4, ("v2f", verts), ("c3B",(int(self.colors[i][0]*0.6),
                                                                                                 int(self.colors[i][1]*0.6),
                                                                                                 int(self.colors[i][2]*0.6))*2 + self.colors[i]*2))]

            verts = [center_x - step / 2, consts.WINDOW_HEIGHT-100,
                     center_x + step / 2, consts.WINDOW_HEIGHT-100,
                     center_x + step / 2, consts.WINDOW_HEIGHT,
                     center_x - step / 2, consts.WINDOW_HEIGHT]
            self.background_graphics += [pyglet.graphics.vertex_list(4, ("v2f", verts), ("c3B", (int(self.colors[i][0]*0.6),
                                                                                                 int(self.colors[i][1]*0.6),
                                                                                                 int(self.colors[i][2]*0.6))*4))]
            verts = [center_x - step / 2, consts.WINDOW_HEIGHT - 100,
                     center_x + step / 2, consts.WINDOW_HEIGHT - 100,
                     center_x + step / 2, consts.WINDOW_HEIGHT - 250,
                     center_x - step / 2, consts.WINDOW_HEIGHT - 250]
            self.background_graphics += [
                pyglet.graphics.vertex_list(4, ("v2f", verts), ("c3B", (int(self.colors[i][0] * 0.2),
                                                                        int(self.colors[i][1] * 0.2),
                                                                        int(self.colors[i][2] * 0.2)) * 4))]
            self.background_elements += [pyglet.text.Label("PLAYER " + str(i+1),
                                                           font_name="impact",
                                                           font_size=40,
                                                           x=center_x,
                                                           y=consts.WINDOW_HEIGHT-80,
                                                           align="center",
                                                           bold=True,
                                                           color=(20, 20, 20, 255),
                                                           anchor_x="center")]
            self.background_elements += [pyglet.text.Label("PLAYER " + str(i + 1),
                                                           font_name="impact",
                                                           font_size=40,
                                                           x=center_x,
                                                           y=consts.WINDOW_HEIGHT - 75,
                                                           align="center",
                                                           bold=True,
                                                           color=(240, 240, 240, 255),
                                                           anchor_x="center")]
            self.money_labels += [pyglet.text.Label("$00000",
                                                    font_name="impact",
                                                    font_size=60,
                                                    x=center_x,
                                                    y=consts.WINDOW_HEIGHT - 200,
                                                    align="center",
                                                    bold=True,
                                                    color=(240, 240, 240, 255),
                                                    anchor_x="center")]

        pass

    def update(self, dt):
        step = 260
        for i in range(self.num_players):
            #print(i)
            center_x = consts.WINDOW_WIDTH / 2 - self.num_players / 2 * (step + 15) + (i+.5) * (step + 15)
            if self.money_amount[i] < self.total_scores[i]:
                self.money_amount[i] += dt*self.ANIMATION_SCALE
                if self.money_amount[i] > self.total_scores[i]:
                    self.money_amount[i] = self.total_scores[i]
                if self.money_amount[i] // 20 >= self.stack_sizes[i]:
                    self.stack_sprites += [pyglet.sprite.Sprite(self.money_image,
                                                                center_x,
                                                                self.stack_tops[i],
                                                                batch=self.stacks)]
                    self.stack_sizes[i] += 1
                    self.stack_tops[i] += 20
                txt = str(int(self.money_amount[i]))
                while len(txt) < 5:
                    txt = "0"+txt
                txt = "$"+txt
                self.money_labels[i].text = txt
        max_top = 0
        for top in self.stack_tops:
            if top > max_top:
                max_top = top
        if max_top > consts.WINDOW_HEIGHT-300:
            for i in range(self.num_players):
                self.stack_tops[i] -= 20
            for sprite in self.stack_sprites:
                sprite.y -= 20
        print(i)
        print(self.money_amount[i])
        print(self.money_amount[i] % 10)
        print(self.stack_sizes[i])
        pass

    def draw_background(self):
        for element in self.background_graphics:
            element.draw(pyglet.gl.GL_POLYGON)
        for element in self.background_elements:
            element.draw()

    def draw(self):
        self.draw_background()
        self.stacks.draw()
        for lbl in self.money_labels:
            lbl.draw()
        pass
