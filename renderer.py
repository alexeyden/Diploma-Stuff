import numpy as np
from math import *

from vispy import gloo, app

import numpy

class Renderer:
	def __init__(self, size, world):
		self.world = world
		
		self.size = size
		self._init_shaders()
		self._init_vehicle()
		self._init_geometry()
		
		self._points_vbo_list = []
		
		self.draw_minimap = False
		self.draw_points = False
	
	def _init_shaders(self):
		vertex = '''
			attribute vec2 pos;
			attribute vec3 col;
			
			uniform mat3 view;
			
			varying vec3 v_color;
			
			void main() {
				vec3 p = view * vec3(pos, 1.0);
				gl_Position = vec4(p.x, p.y, 0.0, 1.0);
				v_color = col;
			}
		'''
		
		fragment = '''
			varying vec3 v_color;
			void main() {
				gl_FragColor = vec4(v_color, 1.0);
			}
		'''
		
		self._program = gloo.Program(vertex,fragment)
		
		vertex_geom = '''
			attribute vec2 pos;
			attribute vec2 uv;
			
			uniform mat3 view;
			
			varying vec2 v_uv;
			
			void main() {
				vec3 p = view * vec3(pos, 1.0);
				gl_Position = vec4(p.x, p.y, 0.0, 1.0);
				v_uv = uv;
			}
		'''
		
		fragment_geom = '''
			varying vec2 v_uv;
			uniform sampler2D tex;
			void main() {
				gl_FragColor = vec4(texture2D(tex, v_uv).rgb, 1.0);
			}
		'''
		
		self._program_geom = gloo.Program(vertex_geom,fragment_geom)
		
		vertex_points = '''
			attribute vec2 pos;
			uniform mat3 view;
			uniform vec3 color;
			varying vec3 v_color;
			
			void main() {
				vec3 p = view * vec3(pos, 1.0);
				gl_Position = vec4(p.x, p.y, 0.0, 1.0);
				v_color = color;
				gl_PointSize = 4;
			}
		'''
		self._program_points = gloo.Program(vertex_points,fragment)
	
	def _init_geometry(self):
		v = self.world.geometry
		
		tex = gloo.Texture2D(v.data)
		
		geom_vert = self._make_box_data(v.world_size)
		
		geom_uv = np.array([
			[ 0.0, 0.0],
			[ 1.0, 0.0],
			[ 1.0, 1.0],
			
			[ 0.0, 0.0],
			[ 1.0, 1.0],
			[ 0.0, 1.0]
		], np.float32)
		
		self._program_geom['pos'] = gloo.VertexBuffer(geom_vert)
		self._program_geom['uv'] = gloo.VertexBuffer(geom_uv)
		self._program_geom['tex'] = tex
	
	def _init_vehicle(self):
		v = self.world.vehicle
		
		sensors_vert = [
			self._make_box_data((0.1, 0.1), off = sensor.position)
			for sensor in v.sensors
		]
		
		vehicle_vert = np.vstack(
			[self._make_box_data((v.width, v.height))] + sensors_vert
		)
		
		sensors_color = [
			[0.8, 0.1, 0.2] for i in range(0, 6)
			for sensor in v.sensors
		]
		
		vehicle_col = np.array(
			[[0.2, 0.5, 0.2] for i in range(0, 6)] + sensors_color,
		np.float32)
		
		self._program['pos'] = gloo.VertexBuffer(vehicle_vert)
		self._program['col'] = gloo.VertexBuffer(vehicle_col)

	def _make_box_data(self, size, off = (0,0)):
		return np.array([
			[-size[0]/2.0 + off[0], -size[1]/2.0 + off[1]],
			[ size[0]/2.0 + off[0], -size[1]/2.0 + off[1]],
			[ size[0]/2.0 + off[0],  size[1]/2.0 + off[1]],
			
			[-size[0]/2.0 + off[0], -size[1]/2.0 + off[1]],
			[ size[0]/2.0 + off[0],  size[1]/2.0 + off[1]],
			[-size[0]/2.0 + off[0],  size[1]/2.0 + off[1]]
		], np.float32)
	
	def draw(self):
		a = self.world.vehicle.rotation
		p = self.world.vehicle.position
		ratio = self.size[0]/self.size[1]
		
		rot = np.array([
			[cos(a), -sin(a),  0.0],
			[sin(a),  cos(a),  0.0],
			[   0.0,     0.0,  1.0]
		], np.float32)
		
		S = 0.3
		scale = np.array([
			[S, 0.0, 0.0],
			[0.0, ratio * S, 0.0],
			[0.0, 0.0, 1.0]
		], np.float32)
		
		trans = np.array([
			[1.0, 0.0, 0.0],
			[0.0, 1.0, 0.0],
			[p[1], p[0], 1.0]
		], np.float32)
		
		self._program_geom['view'] = np.mat(np.dot(trans, scale))
		self._program_geom.draw('triangles')
		
		self._program['view'] = np.mat(np.dot(rot, scale))
		self._program.draw('triangles')
		
		self._program_points['view'] = np.mat(scale)
		self._program_points['color'] = np.array([0.1, 0.3, 0.1])
		
		vp = self.world.vehicle.position
		
		#ray lines
		gloo.gl.glLineWidth(1.0)
		for sensor in self.world.vehicle.sensors:
			p = sensor.measure()
			self._program_points['pos'] = gloo.VertexBuffer(np.array([[0.0, 0.0], [p[0] + vp[1], p[1] + vp[0]]], np.float32))
			self._program_points.draw('lines')
			
		self._program_points['view'] = np.mat(np.dot(trans, scale))
		
		'''
		gloo.gl.glLineWidth(4.0)
		if hash(self.world.vehicle.known_edges) != self._lines_hash:
			self._cached_lines_vbo = [
				gloo.VertexBuffer(np.array(l, np.float32))
				for l in self.world.vehicle.known_edges
			]
			self._lines_hash = hash(self.world.vehicle.known_edges)
			
		for l in self._cached_lines_vbo:
			self._program_points['pos'] = l
			self._program_points.draw('line_strip')
		'''
		'''
		if self.draw_minimap:
			gloo.gl.glLineWidth(1.0)
			S = 0.05
			scale = np.array([
				[S, 0.0, 0.0],
				[0.0, ratio * S, 0.0],
				[-0.5, 0.8, 1.0]
			], np.float32)
			self._program_points['view'] = np.mat(np.dot(trans, scale))
			for l in self.world.vehicle.known_edges:
				self._program_points['pos'] = gloo.VertexBuffer(np.array(l, np.float32))
				self._program_points.draw('line_strip')
			self._program_points['pos'] = gloo.VertexBuffer(np.array([p[1],p[0]], np.float32))
		'''
		
		if len(self._points_vbo_list) != len(self.world.vehicle.geom_chains):
			#print('adding VBO')
			for i in range(len(self._points_vbo_list), len(self.world.vehicle.geom_chains)):
				self._points_vbo_list.append(gloo.VertexBuffer(np.array(self.world.vehicle.geom_chains[i], np.float32)))
		
		
		self._program_points['color'] = np.array([0.2, 0.8, 0.2])
		for vbo in self._points_vbo_list:
			self._program_points['pos'] = vbo
			self._program_points.draw('points')
	
		self._program_points['color'] = np.array([0.8, 0.2, 0.2])
		for data in self.world.vehicle.buffer_chains:
			self._program_points['pos'] = gloo.VertexBuffer(np.array(data, np.float32))
			self._program_points.draw('points')
		
		'''
		gloo.gl.glLineWidth(4.0)
		self._program_points['color'] = np.array([1.0, 0.2, 1.0])
		for trend in self.world.vehicle.buffer_trends:
			self._program_points['pos'] = gloo.VertexBuffer(np.array(trend, np.float32))
			self._program_points.draw('lines')
		self._program_points['color'] = np.array([0.0, 1.0, 1.0])
		
		for trend in self.world.vehicle.buffer_trends_prev:
			if trend != None:
				self._program_points['pos'] = gloo.VertexBuffer(np.array(trend, np.float32))
				self._program_points.draw('lines')
		'''