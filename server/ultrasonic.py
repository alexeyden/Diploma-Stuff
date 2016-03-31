import threading
import numpy as np
from math import *

from model.cppresponsegridblock import CppResponseGridBlock
from model.responsegrid import  ResponseGrid


class Ultrasonic:
    def __init__(self, builder, block_res=64, block_side=4.0, directions=1):
        builder.buildVehicle(size=(0.5, 1.0), position=[0.0, 0.0], rotation=0.0)

        proto = CppResponseGridBlock(block_res, directions)
        builder.buildGrid(ResponseGrid(block_side, proto))

        self.world = builder.finish()
        self.range_log = dict()
        self.range_log_size = 50

        for sensor in self.world.vehicle.sensors:
            self.range_log[sensor] = []

    def update(self, position, rotation):
        """
            Обновление карты по новой позиции и ориентации (рад)

            :param position: новая позиция (x,y)
            :param rotation: новая ориентация (рад отн. востока)
            :rtype: None
        """

        self.world.vehicle.rotation = rotation
        self.world.vehicle.position = position

        for sensor in self.world.vehicle.sensors:
            self.range_log[sensor].append(sensor.lastRange)
            if len(self.range_log[sensor]) > self.range_log_size:
                self.range_log[sensor].pop(0)
                
            r = sensor.measure()

            if r < sensor.maxRange:
                self.world.grid.update(self.world.vehicle.position, sensor.rotation + sensor.vehicle.rotation, r, sensor.angle, False)
            else:
                self.world.grid.update(self.world.vehicle.position, sensor.rotation + sensor.vehicle.rotation, r, sensor.angle, True)

        self.world.update()

    def get_distances(self):
        distances = {sensor.name: sensor.lastRange for sensor in self.world.vehicle.sensors}
        return distances

    def get_range_log(self):
        range_log = {sensor.name: self.range_log[sensor] for sensor in self.world.vehicle.sensors}
        return range_log

    def get_obstacles(self):
        """
            Возвращает ближайшие препятствия в виде
            массива полигонов

            :rtype: list(list(list(x, y)))
        """

        obstacles = self.world.obstacles
        polygons = [
            [list(vertex[0]) for vertex in poly]
            for poly in obstacles
        ]

        return polygons

    def get_grid(self):
        """
            Возвращает карту ближайшего пространства (4 ближайших блока)
            в виде двумерного массива байтов numpy

            :rtype: numpy.array
        """

        dx = self.world.vehicle.position[0] / self.world.grid.blockSize
        dy = self.world.vehicle.position[1] / self.world.grid.blockSize
        sx = 1 if dx > 0 and modf(dx)[0] > 0.5 or dx < 0 and modf(abs(dx))[0] < 0.5 else -1
        sy = 1 if dy > 0 and modf(dy)[0] > 0.5 or dy < 0 and modf(abs(dy))[0] < 0.5 else -1

        local_pos = [
            divmod(self.world.vehicle.position[0], self.world.grid.blockSize)[0] * self.world.grid.blockSize,
            divmod(self.world.vehicle.position[1], self.world.grid.blockSize)[0] * self.world.grid.blockSize
        ]

        if sx < 0:
            local_pos[0] -= self.world.grid.blockSize
        if sy < 0:
            local_pos[1] -= self.world.grid.blockSize

        pd = [
            (0,  0), (sx, 0),
            (0, sy), (sx, sy)
        ]

        black = np.zeros((self.world.grid.blockProto().side,)*2, dtype=np.uint8)

        opos = self.world.grid.blockPosAt(self.world.vehicle.position)
        images = []
        for p in pd:
            pos = (opos[0] + p[0], opos[1] + p[1])
            if pos in self.world.grid.blocks:
                images.append(np.require(self.world.grid.blocks[pos].poData() * 0xff, np.uint8, 'C'))
            else:
                images.append(black)

        if sy > 0:
            images[0], images[2] = images[2], images[0]
            images[1], images[3] = images[3], images[1]

        if sx < 0:
            images[0], images[1] = images[1], images[0]
            images[2], images[3] = images[3], images[2]

        array = np.hstack((
            np.vstack((images[2], images[0])),
            np.vstack((images[3], images[1]))
        ))

        return dict(
            grid=array,
            size=self.world.grid.blockSize * 2,
            position=(local_pos[0], local_pos[1])
        )


class RangefinderUpdateThread(threading.Thread):
    def __init__(self, freq, ultrasonic):
        threading.Thread.__init__(self)
        self.done = threading.Event()
        self.freq = freq
        self.lock = threading.Lock()
        self.position = (0.0, 0.0)
        self.rotation = 0.0
        self.ultrasonic = ultrasonic

    def run(self):
        while not self.done.wait(1.0/self.freq):
            with self.lock:
                self.ultrasonic.update([0, 0], 0)
