#!/usr/bin/env python3

from distutils.core import setup, Extension, Command
from Cython.Build import cythonize

import os

'''
    Building & installing procedure:
    $ ./setup.py build_ext --inplace
    $ ./setup.py install
'''


class LocalInstallCommand(Command):
    description = "Copy *.so into parent module dir"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        module = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.so')]
        lib_name = self.distribution.ext_modules[0].name
        if len(module) > 0:
            self.copy_file(module[0], os.path.join(os.pardir, lib_name + ".so"))

setup(ext_modules = cythonize(Extension(
    "cppresponsegridblock",
    sources=["cppresponsegridblock.pyx"],
    language="c++",
    extra_compile_args=['-O2', '-std=c++11']
    )),
    cmdclass={
        'install': LocalInstallCommand
    })
