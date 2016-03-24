from distutils.core import setup, Extension
from Cython.Build import cythonize

import os

setup(ext_modules = cythonize(Extension(
	"cppresponsegridblock",
	sources=["cppresponsegridblock.pyx"],
	language="c++",
	extra_compile_args=['-O2', '-std=c++11']
)))

os.system("echo copying..; cp cppresponsegridblock.so ../")
