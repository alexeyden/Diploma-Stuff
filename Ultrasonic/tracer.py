import pyopencl as cl
import pyopencl.array as array
import numpy as np
import cv2

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
		src = np.array(lines, dtype=array.vec.int4) 
		dst = np.zeros(shape=(len(lines)), dtype=array.vec.int2) 
		
		src_buf = cl.Buffer(self.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=src)
		dst_buf = cl.Buffer(self.context, mf.WRITE_ONLY, dst.nbytes)
		
		self.program.trace(self.queue, dst.shape, None, self.glob_image, np.uint32(self.width), np.uint32(self.height), src_buf, dst_buf)
		
		cl.enqueue_copy(self.queue, dst, dst_buf)
		
		print(dst)
		
def main():
	image = cv2.imread('test2.png')
	w,h,b = image.shape
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	ret, image = cv2.threshold(image, 0xcc, 0xff, cv2.THRESH_BINARY)
	image = image.flatten()
	print('init..')
	tr = TracerOpenCL(image, w, h)
	tr.trace([(0, 31, 17, 16)])
	
if __name__ == '__main__':
	main()