import math
import numpy as np
cimport numpy as np

from libc.stdint cimport *

from libcpp cimport bool
from libc.stdlib cimport malloc, free

np.import_array()

cdef extern from "util.hpp":
	cdef cppclass vec2[T]:
		vec2()
		vec2(T,T)
		T operator+(const T&)
		T operator-(const T&)
		double length() const
		T x, y

cdef extern from "cppresponsegridblock.hpp":
	cdef cppclass ResponseGridBlock:
		ResponseGridBlock(unsigned, unsigned)
		
		void update(double,double,double,double,double,bool)
		int side() const
		int angles() const
		
		float* poData() 
		float* prData(unsigned) 
		
		ResponseGridBlock* clone() const
		
cdef class CppResponseGridBlock:
	cdef ResponseGridBlock* thisptr;
	
	def __cinit__(self, unsigned side, unsigned n, CppResponseGridBlock clone = None):
		if clone:
			self.thisptr = clone.thisptr.clone()
		else:
			self.thisptr = new ResponseGridBlock(side, n)
		
	def __dealloc__(self):
		del self.thisptr
		
	def update(self, pos, theta, r, alpha, blackout):
		self.thisptr.update(r, theta, alpha, pos[0], pos[1], blackout)
	
	def poData(self):
		cdef np.npy_intp shape[2]
		shape[0] = <np.npy_intp> self.thisptr.side()
		shape[1] = <np.npy_intp> self.thisptr.side()
		
		return np.PyArray_SimpleNewFromData(2, shape, np.NPY_FLOAT32, <void*> self.thisptr.poData())
		
	def prData(self, index):
		cdef np.npy_intp shape[2]
		shape[0] = <np.npy_intp> self.thisptr.side()
		shape[1] = <np.npy_intp> self.thisptr.side()
		
		return np.PyArray_SimpleNewFromData(2, shape, np.NPY_FLOAT32, self.thisptr.prData(index))
		
	@property
	def n(self):
		return self.thisptr.angles()
	@property
	def side(self):
		return self.thisptr.side()
		
	def clone(self):
		return CppResponseGridBlock(0, 0, self)
	