import numpy as np
from model import cv2
import itertools
from math import *


class World:
    def __init__(self, grid):
        self.vehicle = None
        self.grid = grid
        self.obstacles = []

    def update(self):
        self._update_obstacles()

    def _update_obstacles(self):
        pd = [(0, 0)]

        pos = self.grid.blockPosAt(self.vehicle.position)

        dx = self.vehicle.position[0] / self.grid.blockSize
        dy = self.vehicle.position[1] / self.grid.blockSize

        sx = 1 if dx > 0 and modf(dx)[0] > 0.5 or dx < 0 and modf(abs(dx))[0] < 0.5 else -1
        sy = 1 if dy > 0 and modf(dy)[0] > 0.5 or dy < 0 and modf(abs(dy))[0] < 0.5 else -1

        pd += [(sx, 0), (0, sy), (sx, sy)]

        self.obstacles = []

        for p in pd:
            bpos = (pos[0] + p[0], pos[1] + p[1])

            if not bpos in self.grid.blocks:
                continue

            block = self.grid.blocks[bpos]

            Pthr = int(0.6 * 0xff)
            border = 3

            pmap = np.require(block.poData() * 0xff, np.uint8, 'C')
            ret, pmap = cv2.threshold(pmap, Pthr, 0xff, cv2.THRESH_BINARY)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(border,border))
            pmap = cv2.dilate(pmap, kernel, iterations=1)

            _, obstacles, hier = cv2.findContours(pmap, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(pmap, obstacles, -1, 0xff, border)

            _, obstacles, hier = cv2.findContours(pmap, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

            self.obstacles += [
                np.require(ob, dtype=np.float) * self.grid.blockSize/block.side + np.array(bpos)*self.grid.blockSize for ob in obstacles
            ]


class WorldBuilder:
    def buildGrid(self, grid):
        raise NotImplementedError()

    def buildSensor(self, position, direction):
        raise NotImplementedError()

    def buildVehicle(self, size, position, rotation):
        raise NotImplementedError()

    def finish(self):
        raise NotImplementedError
