# coding: utf-8

import numpy as np
import cv2

class World:
	def __init__(self, grid):
		self.vehicle = None
		self.grid = grid
		self.obstacles = []
		
	def update(self):
		self._updateObstacles()
		
	def _updateObstacles(self):
		Pthr = int(0.6 * 0xff)
		border = 2
		
		block = self.grid.blockAt(self.vehicle.position)
		pmap = np.require(block.poData() * 0xff, np.uint8, 'C')
		ret, pmap = cv2.threshold(pmap, Pthr, 0xff, cv2.THRESH_BINARY)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(border,border))
		pmap = cv2.dilate(pmap, kernel, iterations=1)
		
		#obstacles, hier = cv2.findContours(pmap, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
		#cv2.drawContours(pmap, obstacles, -1, 0xff, border)
		obstacles, hier = cv2.findContours(pmap, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
		
		self.obstacles = [np.require(ob, dtype=np.float) * self.grid.blockSize/block.side for ob in obstacles]
		
class WorldBuilder:
	def buildGrid(self, grid):
		raise NotImplementedError()
	
	def buildSensor(self, position, direction):
		raise NotImplementedError()
	
	def buildVehicle(self, size, position, rotation):
		raise NotImplementedError()

	def finish(self):
		raise NotImplementedError