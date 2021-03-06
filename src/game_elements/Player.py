from src.utils import Control
import pyglet
import pymunk
from pymunk.vec2d import Vec2d


class Player:
    def __init__(self, player_id, pos_x, pos_y, rotation,  space):
        self.MASS = 10
        self.MAX_SPEED = 300
        self.FRICTION = 6
        self.LAT_BREAK_FACTOR = 20
        self.ANGULAR_SPEED = 6
        self.position = Vec2d(0, 0)
        self.rotation = 0
        self.player_id = player_id
        self.FUEL_SCALE = 0.002
        self.power_up = None
        self.accelerator_bonus = False
        self.accelerator_timer = -1
        self.is_oiled = False
        self.oiled_timer = -1
        self.apply_invert = False
        self.is_inverted = False
        self.invert_timer = -1
        self.inverted_timer = -1
        self.apply_teleport = False
        self.teleport_timer = -1
        self.wear_off = False
        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()

        graphics = pyglet.resource.image("Players/Player"+str(player_id)+".png")
        graphics.anchor_x = graphics.width // 2
        graphics.anchor_y = graphics.height // 2
        self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(graphics)
        self.body = pymunk.Body(self.MASS, pymunk.moment_for_box(self.MASS, (2*21, 2*9)))
        self.poly = pymunk.Poly.create_box(self.body, (2*21, 2*9))
        space.add(self.body, self.poly)
        self.body.angle = rotation
        self.drive_angle = 0
        self.body.position = Vec2d(pos_x, pos_y)

        self.fuel = 1
        self.money = 0
        self.power_up = None

    def update(self, dt):
        if self.accelerator_timer != -1:
            if self.accelerator_timer > 0:
                self.accelerator_timer -= dt
            else:
                self.accelerator_timer = -1
                self.accelerator_bonus = False
        if self.oiled_timer != -1:
            if self.oiled_timer > 0:
                self.oiled_timer -= dt
            else:
                self.oiled_timer = -1
                self.is_oiled = False
                self.wear_off = True
        if self.invert_timer != -1:
            if self.invert_timer > 0:
                self.invert_timer -= dt
            else:
                self.invert_timer = -1
                self.apply_invert = False
                self.wear_off = True
        if self.inverted_timer != -1:
            if self.inverted_timer > 0:
                self.inverted_timer -= dt
            else:
                self.inverted_timer = -1
                self.is_inverted = False
                self.wear_off = True
        if self.teleport_timer != -1:
            if self.teleport_timer > 0:
                self.teleport_timer -= dt
            else:
                self.teleport_timer = -1
                self.apply_teleport = False
                self.wear_off = True
        local_velocity = self.body.velocity_at_local_point(Vec2d.zero()).rotated(-self.body.angle)
        forward_velocity = local_velocity.dot(Vec2d(1, 0))
        front_wheel_velocity = self.body.velocity_at_local_point(Vec2d(130/8, 0)).rotated(-self.body.angle)
        back_wheel_velocity = self.body.velocity_at_local_point(Vec2d(-130/8, 0)).rotated(-self.body.angle)
        # handling controls
        target_direction = Vec2d(0, 0)
        target_direction.y += Control.control.get_axis("Up"+str(self.player_id))
        target_direction.y -= Control.control.get_axis("Down" + str(self.player_id))
        target_direction.x -= Control.control.get_axis("Left" + str(self.player_id))
        target_direction.x += Control.control.get_axis("Right" + str(self.player_id))
        if self.is_inverted:
            target_direction *= -1
        if abs(target_direction.x) > abs(target_direction.y):
            target_direction = target_direction.normalized()*abs(target_direction.x)
        else:
            target_direction = target_direction.normalized()*abs(target_direction.y)
        if target_direction.length < 0.1:
            target_direction = Vec2d.zero()
        impulse = Vec2d(0, 0)
        if self.accelerator_bonus:
            max_speed = 2 * self.MAX_SPEED
        else:
            max_speed = self.MAX_SPEED
        if forward_velocity < max_speed:
            impulse += dt*Vec2d(1, 0)*(max_speed - forward_velocity)*self.body.mass*target_direction.length
            dfuel = -impulse.length*self.FUEL_SCALE/max_speed
            if dfuel >=0:
                dfuel = -1/(300)*dt
            self.fuel += dfuel
            if self.fuel <= 0:
                self.fuel = 0
                impulse = Vec2d.zero()
        if self.is_oiled:
            friction = self.FRICTION // 6
        else:
            friction = self.FRICTION
        if impulse != Vec2d.zero():
            impulse += friction*dt*Vec2d(0, 1)*local_velocity.dot(Vec2d(0, -1))*self.body.mass
        else:
            impulse += -friction*dt*local_velocity*self.body.mass
        self.body.apply_impulse_at_local_point(impulse, Vec2d.zero())

        if target_direction.length > 0.1 and self.fuel > 0:
            target_angle = target_direction.angle-self.body.angle
            while target_angle > 3.141592:
                target_angle = -2*3.141592 + target_angle
            while target_angle < -3.141592:
                target_angle = 2*3.141592 + target_angle
            self.body.angular_velocity = \
                2*target_angle*self.ANGULAR_SPEED*(forward_velocity + 0.1*self.MAX_SPEED)/self.MAX_SPEED
            if abs(self.body.angular_velocity) > self.ANGULAR_SPEED:
                self.body.angular_velocity = \
                    self.body.angular_velocity*self.ANGULAR_SPEED/abs(self.body.angular_velocity)
        else:
            self.body.angular_velocity *= 0.8
        # updating graphics
        self.sprite.position = (self.body.position.x, self.body.position.y)
        self.sprite.rotation = 90-self.body.angle*57.2957795131  # Radians to degrees conversion
        pass

    def draw(self):
        self.sprite.draw()
        pass
