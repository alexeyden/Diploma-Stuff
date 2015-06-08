import math
import numpy as np
cimport numpy as np
from libc.stdint cimport *

np.import_array()

cdef extern from "util.hpp":
	cdef cppclass vec2[T]:
		vec2()
		vec2(T,T)
		T operator+(const T&)
		T operator-(const T&)
		double length() const
		T x, y

cdef extern from "responsegrid.hpp":
	cdef cppclass ResponseGrid:
		ResponseGrid(unsigned, unsigned, float)
		
		void update(double,double,double,double,double)
		unsigned width() const
		unsigned height() const
		double scale() const
		unsigned angles() const
		
		vec2[int] world2grid(const vec2[double]&)
		vec2[double] grid2world(const vec2[int]&)
		
		uint8_t* poData() 
		uint8_t* prData(unsigned) 
		
cdef class ResponseGridNative:
	cdef ResponseGrid* thisptr;
	
	def __cinit__(self, unsigned width, unsigned height, float scale):
		self.thisptr = new ResponseGrid(width, height, scale)
		
	def __dealloc__(self):
		del self.thisptr
		
	def update(self, sensor):
		point = sensor.measure()
		R = math.sqrt(point[0]*point[0] + point[1]*point[1])
		pos = sensor.vehicle.position
		rot = sensor.vehicle.rotation + sensor.rotation
		
		self.thisptr.update(R, rot, sensor.angle, pos[0], pos[1])
	
	def width(self):
		return self.thisptr.width()
	def height(self):
		return self.thisptr.height()
	def scale(self):
		return self.thisptr.scale()
	def angles(self):
		return self.thisptr.angles()
	
	def world2grid(self, wp):
		gp = self.thisptr.world2grid(vec2[double](wp[0], wp[1]))
		return [gp.x, gp.y]
	def grid2world(self, gp):
		wp = self.thisptr.grid2world(vec2[int](gp[0], gp[1]))
		return [wp.x, wp.y]
	
	def poData(self):
		cdef np.npy_intp shape[2]
		shape[0] = <np.npy_intp> self.thisptr.width()
		shape[1] = <np.npy_intp> self.thisptr.height()
		
		return np.PyArray_SimpleNewFromData(2, shape, np.NPY_UINT8, self.thisptr.poData())
		
	def prData(self, index):
		cdef np.npy_intp shape[2]
		shape[0] = <np.npy_intp> self.thisptr.width()
		shape[1] = <np.npy_intp> self.thisptr.height()
		
		return np.PyArray_SimpleNewFromData(2, shape, np.NPY_UINT8, self.thisptr.prData(index))
	