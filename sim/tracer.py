from math import *

import pyopencl as cl
import pyopencl.array as array
import numpy as np
import cv2

from model.util import *


class TracerStrategy:
    def __init__(self, image):
        self.image = image

    def trace(self, pos, dirs):
        raise NotImplementedError()

class PythonTracer(TracerStrategy):
    def __init__(self, image):
        TracerStrategy.__init__(self, image)

    def trace(self, pos, dirs):
        lens = []
        for d in dirs:
            lens.append(self._traceDir(pos, d))
        return np.array(lens, dtype=np.float32)

    def _traceDir(self, pos, dr):
        dirX = dr[0] + 0.0001
        dirY = dr[1] + 0.0001
        x1,y1 = pos
        x,y = pos

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

        while x > 0 and y > 0 and x < self.image.shape[0]-1 and y < self.image.shape[1]-1 and self.image[y, x] != 0x00:
            if sdx < sdy:
                sdx += ddx
                x += stepX
            else:
                sdy += ddy
                y += stepY

        return np.linalg.norm([x - x1, y - y1])

class OpenCLTracer(TracerStrategy):
    def __init__(self, image):
        TracerStrategy.__init__(self, image)

        self.context = cl.create_some_context()
        self.queue = cl.CommandQueue(self.context)
        f = open('sim/opencl/tracer.cl')
        prog_text = f.read()
        f.close()

        image = image.flatten()

        mf = cl.mem_flags
        self.image_buf = cl.Buffer(self.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=image)
        self.program = cl.Program(self.context, prog_text).build()

    def trace(self, pos, dirs):
        mf = cl.mem_flags
        src = np.array(dirs, dtype=array.vec.float2)
        dst = np.zeros(shape=(len(dirs)), dtype=np.float32)

        src_buf = cl.Buffer(self.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=src)
        dst_buf = cl.Buffer(self.context, mf.WRITE_ONLY, dst.nbytes)
        self.program.trace(self.queue, dst.shape, None, self.image_buf,
                                         np.int32(self.image.shape[0]), np.int32(self.image.shape[1]), np.int32(pos[0]), np.int32(pos[1]),
                                         src_buf, dst_buf)

        cl.enqueue_copy(self.queue, dst, dst_buf)

        return dst

def test():
    import time

    image = cv2.imread('sim/data/world_small.png')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    print('init..')
    tr_py = PythonTracer(image)
    tr_cl = OpenCLTracer(image)
    dirs = [
        (cos(0 * pi/ 180.0), sin(0 * pi / 180.0)),
        (cos(5 * pi/ 180.0), sin(5 * pi / 180.0)),
        (cos(10 * pi/ 180.0), sin(10 * pi / 180.0)),
        (cos(15 * pi/ 180.0), sin(15 * pi / 180.0)),
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
        (0.0, 1.0)
    ]
    print('Python tracer: ')
    ticks = time.clock()
    print(tr_py.trace([356,256], dirs))
    print('Time: {0}'.format(time.clock() - ticks))

    print('OpenCL tracer: ')
    ticks = time.clock()
    print(tr_cl.trace([356,256], dirs))
    print('Time: {0}'.format(time.clock() - ticks))

if __name__ == "__main__":
    test()
