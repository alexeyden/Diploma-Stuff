from model.util import *
from math import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import time
from math import *


class Renderer:
    """
        Визуализатор мира
    """
    def __init__(self, world):
        self.world = world
        self.ppm = 100

    def update(self, area):
        raise NotImplementedError

    def render(self, context):
        raise NotImplementedError

class QPainterRenderer(Renderer):
    def __init__(self, world):
        Renderer.__init__(self, world)

        w,h = self.world.obstacleMap.shape
        self.overlay = QImage(self.world.obstacleMap.data, w, h, QImage.Format_Indexed8)
        for i in range(256):
            self.overlay.setColor(i, QColor(255, 255, 255).rgb())
        self.overlay.setColor(0, QColor(255, 0, 0).rgb())

        self._gridImages = dict()

        self._lastTick = 0
        self._ticksCount = 0

        self.update()

    def update(self):
        pd = [(0, 0)]

        self._gridImages.clear()

        dx = self.world.vehicle.position[0] / self.world.grid.blockSize
        dy = self.world.vehicle.position[1] / self.world.grid.blockSize
        sx = 1 if dx > 0 and modf(dx)[0] > 0.5 or dx < 0 and modf(abs(dx))[0] < 0.5 else -1
        sy = 1 if dy > 0 and modf(dy)[0] > 0.5 or dy < 0 and modf(abs(dy))[0] < 0.5 else -1

        pd += [(sx, 0), (0, sy), (sx, sy)]

        opos = self.world.grid.blockPosAt(self.world.vehicle.position)

        for p in pd:
            pos = (opos[0] + p[0], opos[1] + p[1])

            block = None
            if pos in self.world.grid.blocks:
                block = self.world.grid.blocks[pos]

            if not block:
                continue

            img = np.require(block.poData() * 0xff, np.uint8, 'C')
            self._gridImages[pos] = QImage(img.data, img.shape[0], img.shape[1], QImage.Format_Indexed8)

            for i in range(256):
                self._gridImages[pos].setColor(i, QColor(i, i, i).rgb())

    def _drawGrid(self, context):
        for pos, img in self._gridImages.items():
            context.drawImage(
                QRectF(
                    pos[0] * self.world.grid.blockSize * self.ppm,
                    pos[1] * self.world.grid.blockSize * self.ppm,
                    self.world.grid.blockSize * self.ppm, self.world.grid.blockSize * self.ppm),
                img,
                QRectF(0, 0, img.width(), img.height()))

    def _drawOverlay(self, context):
        if self.overlay:
            context.setOpacity(0.3)
            context.drawImage(QPointF(-self.overlay.width()/2, -self.overlay.height()/2), self.overlay)
            context.setOpacity(1.0)

    def _drawObstacles(self, context):
        context.setPen(QColor(255, 255, 0))

        for i,c in enumerate(self.world.obstacles):
            prev = c[0]
            for p in c[1:]:
                context.drawLine(prev[0][0] * self.ppm, prev[0][1] * self.ppm, p[0][0] * self.ppm, p[0][1] * self.ppm)
                prev = p
            context.drawLine(c[0][0][0] * self.ppm, c[0][0][1] * self.ppm, c[-1][0][0] * self.ppm, c[-1][0][1] * self.ppm)

    def _drawVehicle(self, context):
        vehicle = self.world.vehicle
        context.fillRect(QRectF(
                -vehicle.width/2 * self.ppm, -vehicle.height/2 * self.ppm,
                vehicle.width * self.ppm, vehicle.height * self.ppm
            ), QColor(40, 200, 40))
        context.setPen(QColor(255, 0, 255))
        sensor_size = 5
        for sensor in vehicle.sensors:
            context.fillRect(QRectF(
                sensor.position[0] * self.ppm - sensor_size/2, sensor.position[1] * self.ppm - sensor_size/2,
                sensor_size, sensor_size), QColor(200, 40, 40))
            context.drawPie(QRectF(
                -sensor.lastRange * self.ppm,
                -sensor.lastRange * self.ppm,
                sensor.lastRange * self.ppm * 2,
                sensor.lastRange * self.ppm * 2),
                -to_deg(sensor.rotation - sensor.angle/2) * 16, -to_deg(sensor.angle) * 16)

    def _drawInfo(self, context):
        context.setPen(QColor(20, 20, 20))

        height = 15 * len(self.world.log) + 20
        context.drawRect(10, 10, 200, height)
        context.fillRect(10, 10, 200, height, QColor(0xff, 0xff, 0xff, 0x50))

        for i,item in enumerate(self.world.log.items()):
            context.drawText(QPointF(20, 30 + i*15), '{0}: {1}'.format(item[0],item[1]))

    def _drawMinimap(self, context):
        vehicle = self.world.vehicle
        view_w,view_h = context.viewport().width(), context.viewport().height()
        context.setPen(QColor(20, 20, 20))
        context.drawRect(view_w - 110, 10, 100, 100)
        if self.overlay:
            context.setOpacity(0.3)
            context.drawImage(QRectF(view_w - 110, 10, 100, 100), self.overlay, QRectF(0, 0, self.overlay.width(), self.overlay.height()))
            mpos = [
                (vehicle.position[0] * self.ppm + self.overlay.width()/2) * 100/self.overlay.width(),
                (vehicle.position[1] * self.ppm + self.overlay.height()/2) * 100/self.overlay.height(),
            ]
            context.setOpacity(1.0)
            context.setBrush(QColor(80, 0xff, 40))
            context.drawEllipse(view_w - 110 - 2 + mpos[0], 10 - 2 + mpos[1], 4, 4)

    def render(self, context):
        painter = context
        vehicle = self.world.vehicle

        worldTransform = QTransform()
        worldTransform.translate(painter.viewport().width()/2, painter.viewport().height()/2)
        painter.setWorldTransform(worldTransform)

        painter.rotate(-vehicle.rotation * 180.0/pi)
        painter.translate(-vehicle.position[0] * self.ppm, -vehicle.position[1] * self.ppm)

        self._drawGrid(painter)
        self._drawOverlay(painter)
        self._drawObstacles(painter)

        painter.resetTransform()
        painter.setWorldTransform(worldTransform)

        self._drawVehicle(painter)

        painter.resetTransform()

        self._drawInfo(painter)
        self._drawMinimap(painter)

        self._ticksCount += 1

        if self._ticksCount > 10:
            self.world.log['fps'] = '{0:.2f}'.format(self._ticksCount/(time.clock() - self._lastTick))
            self._ticksCount = 0
            self._lastTick = time.clock()
