from math import cos,sin
from util import *
from functools import reduce

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
import cv2
from util import *

import time

from responsegrid import ResponseGridNative
from tracer import OpenCLTracer 

class Sensor:
	def __init__(self, vehicle, position, rotation):
		self.vehicle = vehicle
		self.position = position
		self.rotation = rotation
		self.angle = to_rad(30) 
		
	def measure(self):
		veh_pos = self.vehicle.position
		dirs = [vec_from_angle(self.rotation + self.vehicle.rotation + to_rad(i * 5)) for i in range(-3, 4)]
		dists = self.vehicle.world.distances(veh_pos, dirs)
		return min(dists)

class Vehicle:
	def __init__(self, world, position, rotation):
		self.width = 40
		self.height = 60
		self.position = position
		self.rotation = rotation
		self.sensors = []
		
		self.world = world
		
class ResponseGrid:
	def __init__(self, width, height, scale):
		self._width = width
		self._height = height
		self._scale = scale
		
		self.angleStep = 22.5
		
		n = int(360/self.angleStep)
		
		self.poMap = np.full((width, height), prob2byte(0.5), dtype=np.uint8)
		self.prMap = []
		
		for i in range(0, int(n)):
			self.prMap.append(np.full((width, height), int((1 - 0.5**(1.0/n)) * 0xff), dtype=np.uint8))
	
	def update(self, sensor):
		theta = sensor.rotation + sensor.vehicle.rotation
		alpha = sensor.angle
		
		R = sensor.measure() + 0.0001
		OA = [ R * cos(theta + alpha/2), R * sin(theta + alpha/2) ]
		OB = [ R * cos(theta - alpha/2), R * sin(theta - alpha/2) ]
		OC = [ R * cos(theta), R * sin(theta) ]
		
		spos = sensor.vehicle.position 
		
		OAg = self._world2grid([OA[0] + spos[0], OA[1] + spos[1]])
		OBg = self._world2grid([OB[0] + spos[0], OB[1] + spos[1]])
		
		P = self._world2grid([ int(min(0, OA[0], OB[0], OC[0]) + spos[0]), int(max(0, OA[1], OB[1], OC[1]) + spos[1]) ])
		Q = self._world2grid([ int(max(0, OA[0], OB[0], OC[0]) + spos[0]), int(min(0, OA[1], OB[1], OC[1]) + spos[1]) ])
		P = [ max(0, min(P[0], self._width-1)), max(0, min(P[1], self._height-1))]
		Q = [ max(0, min(Q[0], self._width-1)), max(0, min(Q[1], self._height-1))]
		
		for x in range(P[0], Q[0]+1):
			for y in range(Q[1], P[1]+1):
				x_loc,y_loc = vec_sub(self._grid2world([x,y]), spos)
				
				if  (x_loc * OA[1] - y_loc * OA[0] >= 0) and (x_loc * OB[1] - y_loc * OB[0] <= 0) and (x_loc**2 + y_loc**2 <= R**2):
						self._updateCell(int(x), int(y), sqrt(x_loc**2 + y_loc**2), R, theta, alpha)
						
	def width(self):
		return self._width
	
	def height(self):
		return self._height
	
	def scale(self):
		return self._scale
	
	def poData(self):
		return self.poMap
	
	def prData(self, index):
		return self.prMap[index]
						
	def _world2grid(self, wp):
		return [int(wp[0] * self._scale + self._width/2), int(wp[1] * self._scale + self._height/2)]
	
	def _grid2world(self, gp):
		return [(gp[0] - self._width/2) / self._scale, (gp[1] - self._height/2) / self._scale]
	
	def _updateCell(self, x, y, s, r, theta, alpha):
		n = int(360/self.angleStep)
		theta_i = int(to_deg(theta)/self.angleStep)
		
		if theta_i < 0 or theta_i >= n:
			print('FIXME: theta_i = ', theta_i)
		
		a = 5.0/alpha#30.0/alpha
		
		Ps = 0.05 if abs(s - r) > 1.0/self._scale else min(1.0, a/(r * self._scale))
		Pp = byte2prob(self.prMap[theta_i][y, x])
		Pn = min(Ps * Pp / (Ps * Pp + (1 - Ps)*(1 - Pp) + 0.01), 1.0)
		
		self.prMap[theta_i][y, x] = prob2byte(Pn)
		
		Po = 1.0 - reduce(lambda x,y: x * y, [1.0 - byte2prob(self.prMap[i][y, x]) for i in range(0, n)])
		self.poMap[y, x] = prob2byte(Po)
	
class World:
	def __init__(self):
		self.vehicle = None
		self.grid = ResponseGrid(128, 128, 0.25)
		self.contours = []

	def distances(self, point, directions):
		raise NotImplementedError
	
	def update(self):
		pmap = np.copy(self.grid.poData())
		ret, pmap = cv2.threshold(pmap, prob2byte(0.55), 0xff, cv2.THRESH_BINARY)
		self.contours,hier = cv2.findContours(pmap, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
		cv2.drawContours(pmap, self.contours, -1, 0xff, 2)
		self.contours,hier = cv2.findContours(pmap, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE, offset=(-self.grid.width()/2, -self.grid.height()/2))
		
		for c in self.contours:
			for p in c:
				p[0][0] /= self.grid.scale(); p[0][1] /= self.grid.scale()
				
class SimulatorWorld(World):
	def __init__(self, geometry):
		World.__init__(self)
		
		self.geometry = geometry
		self.geometryScale = 2
		self.tracer = OpenCLTracer(self.geometry)
	
	def distances(self, point, directions):
		return self.tracer.trace(self.world2geom(point), directions)
	
	def geom2world(self, geom_pos):
		return [
			geom_pos[0] - self.geometry.shape[0]/2,
			geom_pos[1] - self.geometry.shape[1]/2
		]
	
	def world2geom(self, world_pos):
		return [
			world_pos[0] + self.geometry.shape[0]/2,
			world_pos[1] + self.geometry.shape[1]/2
		]
	
class WorldBuilder:
	def buildSensor(self, position, direction):
		raise NotImplementedError
	
	def buildVehicle(self, position, rotation):
		raise NotImplementedError

	def finish(self):
		raise NotImplementedError
		
class SimulatorWorldBuilder(WorldBuilder):
	def __init__(self):
		self.vehicle = None
		self.sensors = []
		self.geometry = None
		self.world = None
	
	def buildSensor(self, position, direction):
		self.sensors.append(Sensor(self.vehicle, position, direction))
	
	def buildVehicle(self, position, rotation):
		self.vehicle = Vehicle(self.world, position, rotation)
		
	def buildGeometry(self, geom):
		self.geometry = geom
	
	def finish(self):
		self.world = SimulatorWorld(self.geometry)
		self.vehicle.world = self.world
		for sensor in self.sensors:
			sensor.vehicle = self.vehicle
		self.vehicle.sensors = self.sensors
		self.world.vehicle = self.vehicle
		
		return self.world
