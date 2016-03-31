from model.world import *
from model.vehicle import *
from .sensor import *


class RobotWorldBuilder(WorldBuilder):
    def __init__(self):
        self.vehicle = None
        self.sensors = []
        self.grid = None
        self.obstacleMap = None
        self.world = None
        self.port = None
        self.baseurl = None

    def buildSensor(self, position, direction, name=None):
        self.sensors.append(RobotSensor(self.vehicle, position, direction, self.port, name=name))

    def buildVehicle(self, size, position, rotation):
        self.vehicle = Vehicle(size, position, rotation, self.world)

    def buildGrid(self, grid):
        self.grid = grid

    def finish(self):
        self.world = World(self.grid)
        self.vehicle.world = self.world
        for sensor in self.sensors:
            sensor.vehicle = self.vehicle
        self.vehicle.sensors = self.sensors
        self.world.vehicle = self.vehicle

        return self.world
