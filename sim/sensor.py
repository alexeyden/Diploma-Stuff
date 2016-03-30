from model import sensor
from model.util import *


class SimSensor(sensor.Sensor):
    def __init__(self, vehicle, position, rotation):
        sensor.Sensor.__init__(self, vehicle, position, rotation)

        self._trace_dirs = []

        da = to_rad(2)
        a = -self.angle/2
        while a < self.angle/2:
            self._trace_dirs.append(a)
            a += da
        self._trace_dirs[-1] = self.angle/2

    def measure(self):
        veh_pos = self.vehicle.position
        world = self.vehicle.world

        obst_map_pos = np.array(np.array(veh_pos) * 100 + np.array(self.vehicle.world.obstacleMap.shape)/2.0, np.int)
        self.vehicle.world.log['map_pos'] = '{0},{1}'.format(obst_map_pos[0], obst_map_pos[1])

        dirs = [vec_from_angle(self.rotation + self.vehicle.rotation + ang) for ang in self._trace_dirs]

        dists = self.vehicle.world.tracer.trace(obst_map_pos, dirs)
        dist = min(dists)/100.0
        self.lastRange = dist
        return dist
