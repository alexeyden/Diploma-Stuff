from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys


class MainWindow(QWidget):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setWindowTitle("Test")
		
	def sizeHint(self):
		return QSize(800, 600)
	
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
