from math import *
import numpy as np


def vec_from_angle(angle):
    return (cos(angle), sin(angle))


def to_deg(angle):
    deg = angle * 180/pi
    deg = int(deg) % 360

    return deg if deg >= 0 else deg + 360


def to_rad(angle):
    return angle * pi/180