from .util import *


class Sensor:
    """
        Ультразвуковой датчик расстояния
    """
    def __init__(self, vehicle, position, rotation):
        self.vehicle = vehicle
        self.position = position
        self.rotation = rotation
        self.angle = to_rad(30)

        self.lastRange = 0
        self.maxRange = 4

    def measure(self):
        raise NotImplementedError()