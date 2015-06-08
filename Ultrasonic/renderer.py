from model import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

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
		
		self.overlay = None
		self._gridImage = QImage(world.grid.width(), world.grid.height(), QImage.Format_RGB32)
	
		self.update()
	
	def update(self):
		img = np.require(self.world.grid.poData(), np.uint8, 'C')
		w,h = img.shape
		self._gridImage = QImage(img.data, w, h, QImage.Format_Indexed8)
		for i in range(256):
			self._gridImage.setColor(i, QColor(0, i, 0).rgb())
		
		if self.overlay:
			self.overlay.convertFromImage(self.world.geometry.image)
		
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
			painter.drawPixmap(QPointF(-self.overlay.width()/2, -self.overlay.height()/2), self.overlay)
			painter.setOpacity(1.0)
				
		painter.setPen(QColor(255, 255, 0))
		for i,c in enumerate(self.world.contours):
			prev = c[0]
			for p in c[1:]:
				painter.drawLine(prev[0][0], prev[0][1], p[0][0], p[0][1])
				prev = p
			painter.drawLine(c[0][0][0], c[0][0][1], c[-1][0][0], c[-1][0][1])
			
		painter.setPen(QColor(0, 255, 255))
		for i,c in enumerate(self.world.holes):
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
		hit_point = vehicle.sensors[0].measure()
		painter.drawEllipse(QPointF(hit_point[0], hit_point[1]), 10, 10)
		
		sensor_size = 5
		
		for sensor in vehicle.sensors:
			painter.fillRect(QRectF(sensor.position[0] - sensor_size/2, sensor.position[1] - sensor_size/2, sensor_size, sensor_size), QColor(200, 40, 40))
			
		painter.resetTransform()
		painter.drawText(QPointF(10, 10), 'Objects: {0}'.format(len(self.world.contours)))
		