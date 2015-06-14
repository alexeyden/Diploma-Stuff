from math import *
import time

from giscon import GisConnector

class WorldController:
	def __init__(self, world, renderer):
		self.world = world
		self.renderer = renderer
	
	def onForward(self, move):
		raise NotImplementedError
	def onBackward(self, move):
		raise NotImplementedError
	def onTurnLeft(self, turn):
		raise NotImplementedError
	def onTurnRight(self, turn):
		raise NotImplementedError
	def onMeasure(self):
		raise NotImplementedError
	def update(self, dt):
		raise NotImplementedError
	
	def onUpdateGisData(self):
		raise NotImplementedError
	
class SimulatorWorldController(WorldController):
	def __init__(self, world, renderer):
		WorldController.__init__(self, world, renderer)
		
		self._curMoveVel = 0
		self._curTurnVel = 0
		
		self.turnVelocity = 2.0
		self.moveVelocity = 100.0
		
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
		for sensor in self.world.vehicle.sensors:
			self.world.grid.update(sensor)
		self.renderer.update()
		self.world.update()
		
	def update(self, dt):
		self.world.vehicle.rotation += self._curTurnVel * dt
		self.world.vehicle.position[0] += self._curMoveVel * cos(self.world.vehicle.rotation - pi/2) * dt
		self.world.vehicle.position[1] += self._curMoveVel * sin(self.world.vehicle.rotation - pi/2) * dt
		
	def onUpdateGisData(self):
		'''
		self.gis.sendHole([[[-256, -256]], [[-256, 256]], [[256, 256]], [[256, -256]]])
		
		for c in  self.world.contours:
			if len(c) > 10:
				self.gis.sendObject(c)
				
		self.gis.sendPosition(self.world.vehicle.position)
		'''