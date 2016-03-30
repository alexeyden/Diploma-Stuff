import numpy as np
from math import *
from .util import *


class ResponseGridBlock:
    """
        Блок сетки отклика размерами side x side ячеек.
        Одна ячейка сетки содержит вероятности откликов с n различных направлений.
    """
    def __init__(self, side, n = 8):
        self.side = side
        self.n = n

    def update(self, pos, theta, r, alpha, blackout):
        raise NotImplementedError()

    def calculateUpdateArea(self, pos, theta, r, alpha):
        raise NotImplementedError()

    def poData(self):
        raise NotImplementedError()

    def prData(self, index):
        raise NotImplementedError()

    def clone(self):
        raise NotImplementedError()

class PyResponseGridBlock(ResponseGridBlock):
    """
        Реализация блока сетки отклика на Python
    """
    def __init__(self, side, n):
        ResponseGridBlock.__init__(self, side, n)

        self._poMap = np.full((side, side), 0.5, dtype=np.float32)
        self._prMap = []

        for i in range(0, int(self.n)):
            self._prMap.append(np.full((side, side), 1 - 0.5**(1.0/n), dtype=np.float32))

    def update(self, pos, theta, r, alpha, blackout):
        pos = np.array(pos)

        OA = [ r * cos(theta + alpha/2), r * sin(theta + alpha/2) ]
        OB = [ r * cos(theta - alpha/2), r * sin(theta - alpha/2) ]
        OC = [ r * cos(theta), r * sin(theta) ]

        P = [int(min(0, OA[0], OB[0], OC[0]) + pos[0]), int(max(0, OA[1], OB[1], OC[1]) + pos[1])]
        Q = [int(max(0, OA[0], OB[0], OC[0]) + pos[0]), int(min(0, OA[1], OB[1], OC[1]) + pos[1])]

        P = [max(0, min(P[0], self.side - 1)), max(0, min(P[1], self.side - 1))]
        Q = [max(0, min(Q[0], self.side - 1)), max(0, min(Q[1], self.side - 1))]

        for x in range(P[0], Q[0]+1):
            for y in range(Q[1], P[1]+1):
                x_loc,y_loc = np.array([x,y]) - pos

                if	(x_loc * OA[1] - y_loc * OA[0] >= 0) and \
                        (x_loc * OB[1] - y_loc * OB[0] <= 0) and \
                        (x_loc**2 + y_loc**2 <= r**2):
                        self._updateCell(int(x), int(y), sqrt(x_loc**2 + y_loc**2), r, theta, alpha, blackout)

    def _updateCell(self, x, y, s, r, theta, alpha, blackout):
        theta_i = int(to_deg(theta)/(360.0/self.n))

        k = 5.0/(alpha * r)
        eps = 5.0

        Ps = 0.05 if abs(s - r) > eps else min(1.0, max(k, 0.5))
        Pp = self._prMap[theta_i][y, x]
        Pn = min(Ps * Pp / (Ps * Pp + (1 - Ps)*(1 - Pp) + 0.01), 1.0)

        self._prMap[theta_i][y, x] = Pn

        Po = 1.0 - reduce(lambda x,y: x * y, [1.0 - self._prMap[i][y, x] for i in range(0, self.n)])

        self._poMap[y, x] = Po

    def poData(self):
        return self._poMap

    def prData(self, index):
        return self._prMap[index]

    def clone(self):
        newGrid = PyResponseGridBlock(self.side, self.n)
        newGrid._poMap = np.copy(self._poMap)
        for i in range(0, self.n):
            newGrid._prMap[i] = np.copy(self._prMap[i])
        return newGrid
