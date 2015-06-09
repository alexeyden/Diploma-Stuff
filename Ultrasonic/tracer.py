import pyopencl as cl
import pyopencl.array as array
import numpy as np
import cv2
from math import *

class TracerOpenCL:
	def __init__(self, image, w, h):
		self.context = cl.create_some_context()
		self.queue = cl.CommandQueue(self.context)
		self.image = image
		self.width = w
		self.height = h
		f = open('opencl/tracer.cl')
		prog_text = f.read()
		f.close()
		
		mf = cl.mem_flags
		self.glob_image = cl.Buffer(self.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=image)
		self.program = cl.Program(self.context, prog_text).build()
		
	def trace(self, lines):
		mf = cl.mem_flags
		src = np.array(lines, dtype=array.vec.float2) 
		dst = np.zeros(shape=(len(lines)), dtype=np.float32) 
		
		src_buf = cl.Buffer(self.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=src)
		dst_buf = cl.Buffer(self.context, mf.WRITE_ONLY, dst.nbytes)
		self.program.trace(self.queue, dst.shape, None, self.glob_image,
										 np.int32(self.width), np.int32(self.height), np.int32(2), np.int32(2),
										 src_buf, dst_buf)
		
		cl.enqueue_copy(self.queue, dst, dst_buf)
		
		for p in dst:
			print(p)
		
def main():
	image = cv2.imread('test2.png')
	w,h,b = image.shape
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	image = image.flatten()
	print('init..')
	tr = TracerOpenCL(image, w, h)
	print('trace...')
	tr.trace([
		(cos(0 * pi/ 180.0), sin(0 * pi / 180.0)),
		(cos(10 * pi/ 180.0), sin(10 * pi / 180.0)),
		(cos(20 * pi/ 180.0), sin(20 * pi / 180.0)),
		(cos(30 * pi/ 180.0), sin(30 * pi / 180.0)),
		(cos(40 * pi/ 180.0), sin(40 * pi / 180.0)),
		(cos(50 * pi/ 180.0), sin(50 * pi / 180.0)),
		(cos(60 * pi/ 180.0), sin(60 * pi / 180.0)),
		(cos(70 * pi/ 180.0), sin(70 * pi / 180.0)),
		(cos(80 * pi/ 180.0), sin(80 * pi / 180.0)),
		(cos(90 * pi/ 180.0), sin(90 * pi / 180.0)),
		(cos(100 * pi/ 180.0), sin(100 * pi / 180.0)),
		(cos(180 * pi/ 180.0), sin(180 * pi / 180.0)),
	])
	
if __name__ == '__main__':
	main()