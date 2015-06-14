#!/usr/bin/env python2
# coding:utf-8

from PyQt5.QtWidgets import *
import sys
from sim.sim import SimMainWindow

def main():
	app = QApplication(sys.argv)
	window = SimMainWindow()
	window.show()
	sys.exit(app.exec_())
	
if __name__ == "__main__":
	main()