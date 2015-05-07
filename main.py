from vispy import app, gloo, use
use('SDL2')
from model import World,Vehicle,Geometry
from renderer import Renderer
import numpy
from PIL import Image
from math import *

class Window(app.Canvas):
	def __init__(self):
		app.Canvas.__init__(self, keys='interactive')
		
		print('Loading data...')
		img = Image.open('world.png')
		
		self._world = World(Geometry(numpy.array(img), img.size[0], img.size[1]))
		self._renderer = Renderer(self.size, self._world)
		
		self._turn_left = False
		self._turn_right = False
		self._move_forward = False
		self._move_back = False
		
		self._timer = app.Timer('auto', connect = self._update, start = True)
		self._ticks = 0
		
	
	def on_initialize(self, e):
		gloo.set_clear_color('white')
	
	def on_resize(self, e):
		w,h = e.size
		self._renderer.size = e.size
		gloo.set_viewport(0, 0, w, h)
	
	def on_draw(self, e):
		gloo.clear()
		
		self._renderer.draw()
	
	def on_key_press(self, e):
		if e.key.name == 'Left':
			self._turn_left = True
		if e.key.name == 'Right':
			self._turn_right = True
		if e.key.name == 'Up':
			self._move_forward = True
		if e.key.name == 'Down':
			self._move_back = True
			
	def on_key_release(self, e):
		self._turn_left = self._turn_left and not e.key.name == 'Left'
		self._turn_right = self._turn_right and not e.key.name == 'Right'
		self._move_forward = self._move_forward and not e.key.name == 'Up'
		self._move_back = self._move_back and not e.key.name == 'Down'
		
		if e.key.name == 'p':
			self._renderer.draw_points = not self._renderer.draw_points 
		if e.key.name == 'm':
			self._renderer.draw_minimap = not self._renderer.draw_minimap
		if e.key.name == 'f':
			self._world.vehicle.do_filter = not self._world.vehicle.do_filter
		if e.key.name == 'e':
			print('export..', end='')
			try:
				self._world.vehicle.export_points('points.txt')
			except:
				print('failed')
			print('OK')
			
	def _update(self, e):
		self.update()
		
		if self._turn_left:
			self._world.vehicle.rotation -= 0.02
		if self._turn_right:
			self._world.vehicle.rotation += 0.02
		if self._move_forward:
			self._world.vehicle.position[0] -= cos(self._world.vehicle.rotation) * 0.02
			self._world.vehicle.position[1] -= sin(self._world.vehicle.rotation) * 0.02
		if self._move_back:
			self._world.vehicle.position[0] += cos(self._world.vehicle.rotation) * 0.02
			self._world.vehicle.position[1] += sin(self._world.vehicle.rotation) * 0.02

		self._world.vehicle.update()	
	
if __name__ == '__main__':
	Window().show()
	app.run()