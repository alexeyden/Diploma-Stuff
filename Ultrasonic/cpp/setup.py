from distutils.core import setup, Extension
from Cython.Build import cythonize

import os

setup(ext_modules = cythonize(Extension(
	"responsegrid",
	sources=["responsegrid.pyx"],
	language="c++",
	extra_compile_args=['-O3', '-std=c++11']
)))

os.system("cp responsegrid.so ../")