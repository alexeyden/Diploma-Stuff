from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from .view import *
from .controller import *
from model.responsegrid import *
from model.responsegridblock import *
from model.cppresponsegridblock import *

from .world import SimWorldBuilder

from math import *
from model import cv2


class SimMainWindow(QWidget):
    def __init__(self, parent=None):
        super(SimMainWindow, self).__init__(parent)
        self.setWindowTitle("Ultrasonic test")

        builder = SimWorldBuilder()
        builder.buildSensor([0.0, 0.5], pi/2)
        builder.buildSensor([0.0, -0.5], -pi/2)
        builder.buildSensor([0.25, 0], 0)
        builder.buildSensor([-0.25, 0], pi)

        builder.buildVehicle(size=(0.5, 1.0), position=[1.0, 0.0], rotation=0.0)

        image = cv2.imread('sim/data/world.png')
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        builder.buildObstacleMap(image)

        proto = CppResponseGridBlock(64, 1)
        builder.buildGrid(ResponseGrid(4, proto))

        self.world = builder.finish()

        self.renderer = QPainterRenderer(self.world)
        self.renderer.update()

        self.controller = SimController(self.world, self.renderer)

        self.timer = QTimer()
        self.timer.timeout.connect(self.timerTick)
        self.timer.start(20)

        self.rangeUpdateTimer = QTimer()
        self.rangeUpdateTimer.timeout.connect(self.mapUpdateTick)
        self.rangeUpdateTimer.start(100)

        self.gisUpdateTimer = QTimer()
        self.gisUpdateTimer.timeout.connect(self.gisUpdateTick)
        self.gisUpdateTimer.start(5000)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.renderer.render(painter)
        painter.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.controller.onTurnLeft(True)
            event.accept()
        if event.key() == Qt.Key_Right:
            self.controller.onTurnRight(True)
            event.accept()
        if event.key() == Qt.Key_Up:
            self.controller.onForward(True)
            event.accept()
        if event.key() == Qt.Key_Down:
            self.controller.onBackward(True)
            event.accept()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.controller.onTurnLeft(False)
            event.accept()
        if event.key() == Qt.Key_Right:
            self.controller.onTurnRight(False)
            event.accept()
        if event.key() == Qt.Key_Up:
            self.controller.onForward(False)
            event.accept()
        if event.key() == Qt.Key_Down:
            self.controller.onBackward(False)
            event.accept()

    def timerTick(self):
        self.controller.update(20.0/1000.0)
        self.repaint()

    def mapUpdateTick(self):
        self.controller.onMeasure()

    def gisUpdateTick(self):
        self.controller.onUpdateGisData()

    def sizeHint(self):
        return QSize(800, 600)
