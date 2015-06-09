from math import *
import time

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
	
	def onForward(self, move):
		self._curMoveVel = self.moveVelocity if move else 0
	def onBackward(self, move):
		self._curMoveVel = -self.moveVelocity if move else 0
	
	def onTurnLeft(self, turn):
		self._curTurnVel = -self.turnVelocity if turn else 0	
	def onTurnRight(self, turn):
		self._curTurnVel = self.turnVelocity if turn else 0
	
	def onMeasure(self):
		for i in range(0, 4):
			self.world.grid.update(self.world.vehicle.sensors[i])
		self.renderer.update()
		self.world.update()
		
	def update(self, dt):
		self.world.vehicle.rotation += self._curTurnVel * dt
		self.world.vehicle.position[0] += self._curMoveVel * cos(self.world.vehicle.rotation - pi/2) * dt
		self.world.vehicle.position[1] += self._curMoveVel * sin(self.world.vehicle.rotation - pi/2) * dt
		
	def onUpdateGisData(self):
		pass