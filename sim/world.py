from model.world import *
from model.vehicle import * 

from .tracer import *
from .sensor import *


class SimWorld(World):
    def __init__(self, grid, obstacle_map):
        World.__init__(self, grid)

        self.obstacleMap = obstacle_map
        self.tracer = PythonTracer(self.obstacleMap)
        self.log = dict()

class SimWorldBuilder(WorldBuilder):
    def __init__(self):
        self.vehicle = None
        self.sensors = []
        self.grid = None
        self.obstacleMap = None
        self.world = None

    def buildSensor(self, position, direction):
        self.sensors.append(SimSensor(self.vehicle, position, direction))

    def buildVehicle(self, size, position, rotation):
        self.vehicle = Vehicle(size, position, rotation, self.world)

    def buildObstacleMap(self,mp):
        self.obstacleMap = mp

    def buildGrid(self, grid):
        self.grid = grid

    def finish(self):
        self.world = SimWorld(self.grid, self.obstacleMap)
        self.vehicle.world = self.world
        for sensor in self.sensors:
            sensor.vehicle = self.vehicle
        self.vehicle.sensors = self.sensors
        self.world.vehicle = self.vehicle

        return self.world
