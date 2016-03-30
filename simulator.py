#!env python3

from PyQt5.QtWidgets import *
import sys
from sim.sim import SimMainWindow

from model.cppresponsegridblock import CppResponseGridBlock

def main():
	app = QApplication(sys.argv)
	window = SimMainWindow()
	window.show()
	sys.exit(app.exec_())
	
if __name__ == "__main__":
	main()
