#!/usr/bin/python2
# -*- coding: utf-8 -*-
from model import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np

class Renderer:
	def __init__(self, world):
		self.world = world
		
		self.scale = 1
	
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
			self.overlay.setColor(i, QColor(i, i, 0).rgb())
	
		self.update()
	
	def update(self):
		block = self.world.grid.blockAt(self.world.vehicle.position)
		if block:
			img = np.require(self.world.grid.blockAt(self.world.vehicle.position).poData(), np.uint8, 'C')
			w,h = img.shape
			self._gridImage = QImage(img.data, w, h, QImage.Format_Indexed8)
			for i in range(256):
				self._gridImage.setColor(i, QColor(0, i, 0).rgb())
		
		if self.overlay:
			img = np.require(self.world.geometry, np.uint8, 'C')
			w,h = img.shape
			self.overlay = QImage(img, w, h, QImage.Format_Indexed8)
			for i in range(256):
				self.overlay.setColor(i, QColor(0, i, 0).rgb())
		
	def render(self, context):
		painter = context
		vehicle = self.world.vehicle
		
		worldTransform = QTransform()
		worldTransform.translate(painter.viewport().width()/2, painter.viewport().height()/2)
		worldTransform.scale(self.scale, self.scale)
		painter.setWorldTransform(worldTransform)
		
		painter.rotate(-vehicle.rotation * 180.0/pi)
		painter.translate(-vehicle.position[0], -vehicle.position[1])
		
		painter.drawImage(
			QRectF(-self.overlay.width()/2, -self.overlay.height()/2, self.overlay.width(), self.overlay.height()),
			self._gridImage,
			QRectF(0, 0, self._gridImage.width(), self._gridImage.height()))
		
		if self.overlay:
			painter.setOpacity(0.3)
			painter.drawImage(QPointF(-self.overlay.width()/2, -self.overlay.height()/2), self.overlay)
			painter.setOpacity(1.0)
				
		painter.setPen(QColor(255, 255, 0))
		for i,c in enumerate(self.world.contours):
			prev = c[0]
			for p in c[1:]:
				painter.drawLine(prev[0][0], prev[0][1], p[0][0], p[0][1])
				prev = p
			painter.drawLine(c[0][0][0], c[0][0][1], c[-1][0][0], c[-1][0][1])
			
		painter.resetTransform()
		painter.setWorldTransform(worldTransform)
		
		#vehicle
		painter.fillRect(QRectF(-vehicle.width/2, -vehicle.height/2, vehicle.width, vehicle.height), QColor(40, 200, 40))
		
		painter.setPen(QColor(255, 0, 255))
		
		sensor_size = 5
		
		for sensor in vehicle.sensors:
			painter.fillRect(QRectF(sensor.position[0] - sensor_size/2, sensor.position[1] - sensor_size/2, sensor_size, sensor_size), QColor(200, 40, 40))
			
		painter.setPen(QColor(20, 20, 20))
		
		painter.resetTransform()
		painter.fillRect(5, 5, 300, 80, QColor(0xff, 0xff, 0xff, 0x50))
		painter.drawText(QPointF(10, 20), 'Кол-во объектов: {0}'.format(len(self.world.contours)))
		painter.drawText(QPointF(10, 35), 'Позиция (local XY): ({0:.3f}, {1:.3f})'.format(
			self.world.vehicle.position[0],
			self.world.vehicle.position[1]
		))
		painter.drawText(QPointF(10, 50), 'Поворот: {0:.1f}'.format(to_deg(self.world.vehicle.rotation)))
		
		theta_i = int(to_deg(self.world.vehicle.rotation)/(360/8))
		painter.drawText(QPointF(10, 65), 'Theta index: {0}'.format(theta_i))
		
		view_w,view_h = painter.viewport().width(), painter.viewport().height()
		painter.setBrush(QColor(0xff, 0x70, 0x20))
		if self.overlay:
			painter.setOpacity(0.3)
			painter.drawImage(QRectF(view_w - 110, 10, 100, 100), self.overlay, QRectF(0, 0, self.overlay.width(), self.overlay.height()))
			mpos = [
				(vehicle.position[0] + self.overlay.width()/2) * 100/self.overlay.width(),
				(vehicle.position[1] + self.overlay.height()/2) * 100/self.overlay.height(),
			]		 
			painter.setOpacity(1.0)
			painter.drawEllipse(view_w - 110 - 2 + mpos[0], 10 - 2 + mpos[1], 4, 4)
		