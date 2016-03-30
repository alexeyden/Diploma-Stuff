from math import *
from model.util import *


class SimController:
    def __init__(self, world, renderer):
        self.world = world
        self.renderer = renderer

        self._curMoveVel = 0
        self._curTurnVel = 0

        self.turnVelocity = 1
        self.moveVelocity = 1.0

        #self.gis = GisConnector('10.42.0.1')

    def onForward(self, move):
        self._curMoveVel = self.moveVelocity if move else 0
    def onBackward(self, move):
        self._curMoveVel = -self.moveVelocity if move else 0

    def onTurnLeft(self, turn):
        self._curTurnVel = -self.turnVelocity if turn else 0
    def onTurnRight(self, turn):
        self._curTurnVel = self.turnVelocity if turn else 0

    def onMeasure(self):
        for i, sensor in enumerate(self.world.vehicle.sensors):
            r = sensor.measure()
            if r < 4:
                self.world.log['r_' + str(i)] = '{0:.3f}'.format(r)
                self.world.grid.update(self.world.vehicle.position, sensor.rotation + sensor.vehicle.rotation, r, sensor.angle, False)
            else:
                r = 4
                self.world.log['r_' + str(i)] = '> 4 m'
                self.world.grid.update(self.world.vehicle.position, sensor.rotation + sensor.vehicle.rotation, r, sensor.angle, True)

        self.world.update()
        self.renderer.update()

    def update(self, dt):
        self.world.vehicle.rotation += self._curTurnVel * dt
        self.world.vehicle.position[0] += self._curMoveVel * cos(self.world.vehicle.rotation - pi/2) * dt
        self.world.vehicle.position[1] += self._curMoveVel * sin(self.world.vehicle.rotation - pi/2) * dt

        self.world.log['pos'] = '{0:.2f} m,{1:.2f} m'.format(self.world.vehicle.position[0], self.world.vehicle.position[1])
        self.world.log['rot'] = '{0:.2f}'.format(to_deg(self.world.vehicle.rotation))
        self.world.log['grid_pos'] = '{0:.2f},{1:.2f}'.format(
            self.world.vehicle.position[0]/self.world.grid.blockSize,
            self.world.vehicle.position[1]/self.world.grid.blockSize)

    def onUpdateGisData(self):
        '''
        self.gis.sendHole([[[-256, -256]], [[-256, 256]], [[256, 256]], [[256, -256]]])

        for c in  self.world.contours:
            if len(c) > 10:
                self.gis.sendObject(c)

        self.gis.sendPosition(self.world.vehicle.position)
        '''
