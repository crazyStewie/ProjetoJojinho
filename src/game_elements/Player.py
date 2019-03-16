from src.utils import Control
import pyglet
import pymunk
from pymunk.vec2d import Vec2d

class Player:
    def __init__(self, player_id, pos_x, pos_y, rotation,  space):
        self.MASS = 10
        self.MAX_ACCEL = 20
        self.TAN_BREAK_FACTOR = 1/20
        self.LAT_BREAK_FACTOR = 20
        self.MAX_TURN = 0.2
        self.STEER_SPEED = 2.4

        self.position = Vec2d(0,0)
        self.rotation = 0

        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()
        graphics = pyglet.resource.image("red_player.png")
        graphics.anchor_x = graphics.width // 2
        graphics.anchor_y = graphics.height // 2
        self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(graphics)
        self.sprite.scale = 1/8
        self.body = pymunk.Body(self.MASS,pymunk.moment_for_box(self.MASS,(250/8,124/8)))
        self.poly = pymunk.Poly.create_box(self.body,(250/8, 124/8))
        space.add(self.body,self.poly)
        self.body.angle = rotation
        self.drive_angle = 0
        self.body.position = Vec2d(pos_x, pos_y)

    def update(self, dt):
        front_wheel_velocity = self.body.velocity_at_local_point(Vec2d(130/8, 0)).rotated(-self.body.angle)
        back_wheel_velocity = self.body.velocity_at_local_point(Vec2d(-130/8, 0)).rotated(-self.body.angle)
        # handling controls
        if Control.control.is_pressed("ui_left"):
            if self.drive_angle < self.MAX_TURN:
                self.drive_angle += self.STEER_SPEED*dt
            else:
                self.drive_angle = self.MAX_TURN
        if Control.control.is_pressed("ui_right"):
            if self.drive_angle > -self.MAX_TURN:
                self.drive_angle -= self.STEER_SPEED * dt
            else:
                self.drive_angle = -self.MAX_TURN
        if not Control.control.is_pressed("ui_right") and not Control.control.is_pressed("ui_left"):
            if self.drive_angle > 0:
                self.drive_angle -= self.STEER_SPEED*dt
                if self.drive_angle < 0:
                    self.drive_angle = 0
            if self.drive_angle < 0:
                self.drive_angle += self.STEER_SPEED*dt
                if self.drive_angle > 0:
                    self.drive_angle = 0
        if Control.control.is_pressed("ui_up"):
            self.body.apply_impulse_at_local_point(self.MASS*self.MAX_ACCEL*Vec2d(1, 0).rotated(self.drive_angle), Vec2d(130/8, 0))
        elif Control.control.is_pressed("ui_down"):
            self.body.apply_impulse_at_local_point(self.MASS*self.MAX_ACCEL*Vec2d(-0.6, 0).rotated(self.drive_angle), Vec2d(130/8, 0))
        else:
            self.body.apply_impulse_at_local_point(self.MASS*self.TAN_BREAK_FACTOR*Vec2d(-1, 0).rotated(self.drive_angle)*front_wheel_velocity.dot(Vec2d(1, 0).rotated(self.drive_angle)), Vec2d(130/8, 0))

        # handling car behavior
        # front wheel
        lateral_impulse = self.MASS*front_wheel_velocity.dot(Vec2d(0, 1).rotated(self.drive_angle))/12
        #print(front_wheel_velocity)
        #print("front initial = ", lateral_impulse)
        if abs(lateral_impulse) > abs(self.MASS*self.LAT_BREAK_FACTOR):
            lateral_impulse /= abs(lateral_impulse)
            lateral_impulse *= self.MASS*self.LAT_BREAK_FACTOR
        self.body.apply_impulse_at_local_point(Vec2d(0, -1).rotated(self.drive_angle)*lateral_impulse, Vec2d(130/5, 0))
        #print("front lateral impulse = ", lateral_impulse)
        #print(self.drive_angle)

        # back wheel
        lateral_impulse = self.MASS*back_wheel_velocity.dot(Vec2d(0, 1))/12
        #print(back_wheel_velocity)
        #print("back initial = ", lateral_impulse)
        if abs(lateral_impulse) > abs(self.MASS*self.LAT_BREAK_FACTOR):
            lateral_impulse /= abs(lateral_impulse)
            lateral_impulse *= self.MASS * self.LAT_BREAK_FACTOR
        #print("back lateral impulse = ", lateral_impulse)
        self.body.apply_impulse_at_local_point(self.MASS*self.TAN_BREAK_FACTOR*Vec2d(-1, 0)*back_wheel_velocity.dot(Vec2d(1, 0)), Vec2d(-130/8, 0))
        self.body.apply_impulse_at_local_point(Vec2d(0, -1) * lateral_impulse, Vec2d(-130/8, 0))

        # updating graphics
        self.sprite.position = (self.body.position.x, self.body.position.y)
        self.sprite.rotation = -self.body.angle*57.2957795131
        pass

    def draw(self):
        self.sprite.draw()
        pass
