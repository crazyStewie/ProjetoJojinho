from src.utils import Control
import pyglet
import pymunk
from pymunk.vec2d import Vec2d

class Player:
    def __init__(self, player_id, pos_x, pos_y, rotation,  space):
        self.MASS = 10
        self.MAX_SPEED = 450
        self.TAN_BREAK_FACTOR = 1/20
        self.LAT_BREAK_FACTOR = 20
        self.MAX_TURN = 0.6
        self.STEER_SPEED = 2.4
        self.ANGULAR_SPEED = 6
        self.position = Vec2d(0, 0)
        self.rotation = 0
        self.player_id = player_id

        pyglet.resource.path = ["../assets/sprites"]
        pyglet.resource.reindex()

        graphics = pyglet.resource.image("Players/Player"+str(player_id)+".png")
        graphics.anchor_x = graphics.width // 2
        graphics.anchor_y = graphics.height // 2
        self.sprite: pyglet.sprite.Sprite = pyglet.sprite.Sprite(graphics)
        self.sprite.scale = 2
        self.body = pymunk.Body(self.MASS, pymunk.moment_for_box(self.MASS, (2*21, 2*9)))
        self.poly = pymunk.Poly.create_box(self.body, (2*21, 2*9))
        space.add(self.body,self.poly)
        self.body.angle = rotation
        self.drive_angle = 0
        self.body.position = Vec2d(pos_x, pos_y)

    def update(self, dt):
        local_velocity = self.body.velocity_at_local_point(Vec2d.zero()).rotated(-self.body.angle)
        foward_velocity = local_velocity.dot(Vec2d(1, 0))
        front_wheel_velocity = self.body.velocity_at_local_point(Vec2d(130/8, 0)).rotated(-self.body.angle)
        back_wheel_velocity = self.body.velocity_at_local_point(Vec2d(-130/8, 0)).rotated(-self.body.angle)
        # handling controls
        target_direction = Vec2d(0, 0)
        target_direction.y += Control.control.get_axis("Up"+str(self.player_id))
        target_direction.y -= Control.control.get_axis("Down" + str(self.player_id))
        target_direction.x -= Control.control.get_axis("Left" + str(self.player_id))
        target_direction.x += Control.control.get_axis("Right" + str(self.player_id))
        if abs(target_direction.x) > abs(target_direction.y):
            target_direction = target_direction.normalized()*abs(target_direction.x)
        else:
            target_direction = target_direction.normalized()*abs(target_direction.y)
        if target_direction.length < 0.1:
            target_direction = Vec2d.zero()
        impulse = Vec2d(0, 0)
        if foward_velocity < self.MAX_SPEED:
            impulse += dt*Vec2d(1, 0)*(self.MAX_SPEED - foward_velocity)*self.body.mass*target_direction.length
        if impulse != Vec2d.zero():
            impulse += 4*dt*Vec2d(0, 1)*local_velocity.dot(Vec2d(0, -1))*self.body.mass
        else:
            impulse += -4*dt*local_velocity*self.body.mass
        self.body.apply_impulse_at_local_point(impulse, Vec2d.zero())

        if target_direction.length > 0.1:
            target_angle = target_direction.angle-self.body.angle
            while target_angle > 3.141592:
                target_angle = -2*3.141592 + target_angle
            while target_angle < -3.141592:
                target_angle = 2*3.141592 + target_angle
            self.body.angular_velocity = 2*target_angle*self.ANGULAR_SPEED*(foward_velocity + 0.1*self.MAX_SPEED)/self.MAX_SPEED
            if abs(self.body.angular_velocity) > self.ANGULAR_SPEED:
                self.body.angular_velocity = self.body.angular_velocity*self.ANGULAR_SPEED/abs(self.body.angular_velocity)
        else:
            self.body.angular_velocity *= 0.8
        # updating graphics
        self.sprite.position = (self.body.position.x, self.body.position.y)
        self.sprite.rotation = 90-self.body.angle*57.2957795131  # Radians to degrees convertion
        pass

    def draw(self):
        self.sprite.draw()
        pass
