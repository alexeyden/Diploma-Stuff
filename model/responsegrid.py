import numpy as np
from math import *
from .util import *

import time


class ResponseGrid:
    """
        Сетка отклика
        blocks хранит инстанцированные блоки в виде словаря
        (x,y) -> block, где (x,y) - коориднаты в с.к. сетки
        blockSize - размер блока сетки в метрах
    """
    def __init__(self, blockSize, blockProto):
        self.blockSize = blockSize
        self.blocks = dict()

        self._blockProto = blockProto

    def blockProto(self):
        return self._blockProto

    def blockAt(self, pos):
        pos = self.blockPosAt(pos)

        if (pos[0], pos[1]) in self.blocks:
            return self.blocks[(pos[0], pos[1])]
        return None

    def blockPosAt(self, pos):
        return (
            int(floor(pos[0]/self.blockSize)),
            int(floor(pos[1]/self.blockSize))
        )

    def update(self, pos, theta, r, alpha, blackout = False):
        """
            Обновить сетку по новому измерению (theta, r)
            с позиции pos и угловыми размерами конуса alpha
        """
        pos = np.array(pos)
        grid_pos = pos/self.blockSize

        P,Q = self._calculateUpdateArea(grid_pos, theta, r/self.blockSize, alpha)

        for x in range(P[0], Q[0] + 1):
            for y in range(Q[1], P[1] + 1):
                if (x,y) not in self.blocks:
                    self.blocks[(x,y)] = self._blockProto.clone()

                pos_block = (
                    (grid_pos[0] - x) * self._blockProto.side,
                    (grid_pos[1] - y) * self._blockProto.side
                )
                self.blocks[(x,y)].update(pos_block, theta, r * self._blockProto.side/self.blockSize, alpha, blackout)

    def _calculateUpdateArea(self, pos, theta, r, alpha):
        OA = [ r * cos(theta + alpha/2), r * sin(theta + alpha/2) ]
        OB = [ r * cos(theta - alpha/2), r * sin(theta - alpha/2) ]
        OC = [ r * cos(theta), r * sin(theta) ]

        P = [int(floor(min(0, OA[0], OB[0], OC[0]) + pos[0])), int(floor(max(0, OA[1], OB[1], OC[1]) + pos[1]))]
        Q = [int(floor(max(0, OA[0], OB[0], OC[0]) + pos[0])), int(floor(min(0, OA[1], OB[1], OC[1]) + pos[1]))]

        return (P, Q)

if __name__ == '__main__':
    test()
