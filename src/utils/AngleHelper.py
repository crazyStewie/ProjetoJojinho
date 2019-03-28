from math import pi


def angle_to_positive_degrees(angle):
    while angle <= 0:
        angle += 360
    while angle > 360:
        angle -= 360
    return angle


def angle_to_positive(angle):
    while angle <= 0:
        angle += 2*pi
    while angle > 2*pi:
        angle -= 2*pi
    return angle
