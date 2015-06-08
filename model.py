from math import * 
import numpy as np
import concurrent.futures as future
import random
import kalman

class RangeSensor:
	def __init__(self, parent, pos, di):
		self.position = pos
		self.direction = di
		self.parent = parent
		self.prev = []
	
	def measure(self):
		pos_list = []
		
		for dr in range(-15, 15, 3):
			m = self._trace(dr)
			pos_list.append(m)
		
		mes = [
			sum([p[0] for p in pos_list])/len(pos_list),
			sum([p[1] for p in pos_list])/len(pos_list)
		]
		return np.array(mes, np.float32)
	
	def _trace(self, drot):
		drot_rad = pi * drot/180
		
		a = self.parent.rotation
		rot = np.array([
			[cos(a), -sin(a),  0.0],
			[sin(a),  cos(a),  0.0],
			[   0.0,     0.0,  1.0]
		], np.float32)
		
		p = np.array([self.position[0], self.position[1], 1])
		wp = np.dot(rot, p)
		
		a = self.parent.rotation + self.direction + drot_rad
		
		rot = np.array([
			[cos(a), -sin(a),  0.0],
			[sin(a),  cos(a),  0.0],
			[   0.0,     0.0,  1.0]
		], np.float32)
		wpd = np.dot(rot, np.array([0, 1, 1]))
		
		pos_vec = np.array([self.parent.position[1] + wp[1], self.parent.position[0] + wp[0]], np.float32)
		vec = pos_vec + [wpd[1], wpd[0]]
		
		p0 = self._world_to_image(self.parent.position)
		p1 = self._world_to_image(vec)
		x1,y1 = p0
		x2,y2 = p1
		x = int(x1)
		y = int(y1)
		
		points = []
		
		#trace
		dirX = (x2-x1 + 0.0001)/sqrt((x2 - x1)*(x2 - x1) + (y2 - y1) * (y2 - y1))
		dirY = (y2-y1 + 0.0001)/sqrt((x2 - x1)*(x2 - x1) + (y2 - y1) * (y2 - y1))
		
		ddx = sqrt(1 + (dirY * dirY) / (dirX * dirX))
		ddy = sqrt(1 + (dirX * dirX) / (dirY * dirY))
		
		stepX = 1
		stepY = 1
		sdy = 1 * ddy
		sdx = 1 * ddx
		
		if dirX < 0:
			stepX = -1
			sdx = 0
			
		if dirY < 0:
			stepY = -1
			sdy = 0
		
		while x > 0 and y > 0 and x < 511 and y < 511 and self.parent.world.geometry.empty(x, y):
			if sdx < sdy:
				sdx += ddx
				x += stepX
			else:
				sdy += ddy
				y += stepY
		
		error = 0.1
		rand = random.uniform(-error/2, error)
		displ = (rand * (x - x1), rand * (y - y1))
		return self._image_to_world([x + displ[0],y + displ[1]])
	
	def _image_to_world(self, img_vec):
		iw = self.parent.world.geometry.width
		ih = self.parent.world.geometry.height
		return np.array([
			-1 *( (1 - img_vec[0]/iw) * 8.0 - 4.0),
			-1 *( (1 - img_vec[1]/ih) * 8.0 - 4.0),
		], np.float32)
	
	def _world_to_image(self, w_vec):
		iw = self.parent.world.geometry.width
		ih = self.parent.world.geometry.height
		return np.array([
			(1 - (w_vec[0] + 4.0)/8.0) * iw,
			(1 - (w_vec[1] + 4.0)/8.0) * ih
		], np.int32)

class Vehicle:
	def __init__(self):
		self.width = 0.6
		self.height = 0.8
		self.position = [0.0, 0.0]
		self.rotation = 0.0
		self._world = None
		
		self.geom_chains = []
		self.buffer_chains = [[], [], [], []]
		self.buffer_chains_max = [0.0, 0.0, 0.0, 0.0]
		self.do_filter = False
		
		self.prev_r = None
		self.sensors = []
		self.sensors.append(RangeSensor(self,  [-0.3, 0.0], -pi/2))
		self.sensors.append(RangeSensor(self, [ 0.0, 0.4], 0))
		self.sensors.append(RangeSensor(self, [ 0.3, 0.0], pi/2))
		self.sensors.append(RangeSensor(self,  [ 0.0,-0.4], pi))
		
		self.chain_split_thr = 0.5
		
		Q,R,F,B,H = 0.05 * np.eye(2), 1.0 * np.eye(2), np.eye(2), np.eye(2), np.eye(2)
		self._kalman = [
			kalman.KalmanFilter(Q, R, F, B, H) for i in range(0, 4)
		]
		
		#for k in self._kalman:
		#	k.p = 0.2 * np.eye(2)
	
	'''
	def _chain_trend(self, index):
		chain = self.buffer_chains[index]
		
		Mx, My, ap, bp, am, bm = algo.pca2d(chain)
		
		a_len = sqrt(ap*ap + bp*bp)
		max_dist = sqrt((chain[0][0]-chain[-1][0])**2 + (chain[0][1] - chain[-1][1])**2)/2
		
		ap = max_dist * ap / a_len
		bp = max_dist * bp / a_len
		
		start = [-ap + Mx, -bp + My]
		end = [ap + Mx, bp + My]
		
		self.buffer_trends[index] = (start, end)
		return (ap, bp)
	'''
	
	def _add_filtered(self, value, chain, kalman):
		if self.do_filter:
			chain.append(kalman.correct(value))
		else:
			chain.append(value)
	
	def export_points(self, path):
		f = open(path, 'w')
		for chain in self.geom_chains:
			for point in chain:
				f.write('{0:.3f} {1:.3f}\n'.format(point[0], point[1]))
			f.write('\n')
		f.close()
	
	def _should_split(self, point, sensor_id):
		chain = self.buffer_chains[sensor_id]
		m = point
		
		if len(chain) > 0 and np.sqrt(np.dot(m - chain[-1], m - chain[-1])) > self.chain_split_thr:
			return True
		'''
		prev_trend = self.buffer_trends_prev[sensor_id]
		if not prev_trend is None and not trend is None and prev_trend[0] * trend[0] + prev_trend[1] * trend[1] < 0.8:
			return True
		'''
		
		return False
	
	def update(self):
		for i, sensor in enumerate(self.sensors):
			m = sensor.measure()
			
			if len(self.buffer_chains[i]) == 0:
				self._kalman[i].reset(m, np.array([0,0]), 0.2 * np.eye(2))
				self.buffer_chains[i].append(m)
				continue
			'''
			x, y = None, None
			if len(self.buffer_chains[i]) > 5:
				x,y = self._chain_trend(i)
				if len(self.buffer_chains[i]) == 20:
					self.buffer_trends_prev[i] = (x, y)
			'''
			
			dist = sqrt((m[0] - self.buffer_chains[i][0][0])**2 + (m[1] - self.buffer_chains[i][0][1])**2)
			
			if dist > self.buffer_chains_max[i]:
				self.buffer_chains_max[i] = dist

			if self._should_split(m, i):
				if len(self.buffer_chains[i]) > 5:
					self.geom_chains.append(self.buffer_chains[i][:-1])
				self.buffer_chains[i] = []
				#self.buffer_trends_prev[i] = None
				#self.buffer_trends[i] = []
				self._kalman[i].reset(m, np.array([0,0]))#, 0.2 * np.eye(2))
				continue
				#print('splitting chain')
			
			if dist > 0.5:
				self.geom_chains.append(self.buffer_chains[i])
				self.buffer_chains[i] = []
				self.buffer_chains_max[i] = 0.0
			
			if len(self.buffer_chains[i]) < 1 or sqrt((self.buffer_chains[i][-1][0] - m[0])**2 + (self.buffer_chains[i][-1][1] - m[1])**2) > 0.05:
				self._add_filtered(m, self.buffer_chains[i], self._kalman[i])
	
	@property
	def world(self):
		return self._world
	@world.setter
	def world(self, w):
		self._world = w

class Geometry:
	def __init__(self, data, width, height):
		self.data = data
		self.width = width
		self.height = height
		self.world_size = [8, 8]
		self.world = None
		
	def empty(self, x, y):
		v = self.data[int(y)][int(x)]
		return v[0] != 0 or v[1] != 0 or v[2] != 0 

class World:
	def __init__(self, geom):
		self.vehicle = Vehicle()
		self.geometry = geom
		
	@property
	def geometry(self):
		return self._geometry
	@geometry.setter
	def geometry(self, g):
		self._geometry = g
		g.world = self
		
	@property
	def vehicle(self):
		return self._vehicle
	@vehicle.setter
	def vehicle(self, v):
		self._vehicle = v
		v.world = self