#!/usr/bin/python2

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from model import *
from renderer import *
from controller import *

import random
import sys

import numpy as np
import cv2

import time

class TestWindow(QWidget):
	def __init__(self, parent=None):
		super(TestWindow, self).__init__(parent)
		self.setWindowTitle("alg test window")
		
		image = cv2.imread('test.png')
		self.qimage = QImage('test.png')
		self.image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		self.contours,hier = cv2.findContours(self.image, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		painter.drawImage(0, 0, self.qimage)
		
		painter.setPen(QColor(0xffff0000))
		
		for i,c in enumerate(self.contours):
			prev = c[0]
			for p in c[1:]:
				painter.drawLine(prev[0][0], prev[0][1], p[0][0], p[0][1])
				prev = p
			painter.drawLine(c[0][0][0], c[0][0][1], c[-1][0][0], c[-1][0][1])
		
		painter.end()

class MainWindow(QWidget):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setWindowTitle("Ultrasonic test")
		
		builder = SimulatorWorldBuilder()
		builder.buildSensor([0.0, 30], pi/2)
		builder.buildSensor([0.0, -30], -pi/2)
		builder.buildSensor([20, 0], 0)
		builder.buildSensor([-20, 0], pi)
		
		builder.buildVehicle([0.0, 0.0], 0.0)
		
		builder.buildGeometry(QImageGeometry(QImage('../world.png')))
		self.world = builder.finish()
		
		self.renderer = QPainterRenderer(self.world)
		self.renderer.overlay = QPixmap('../world.png')
		self.renderer.update()
		
		self.controller = SimulatorWorldController(self.world, self.renderer)
		
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
	
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
