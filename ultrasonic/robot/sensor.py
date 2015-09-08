from model import sensor
from model.util import *

class RobotSensor(sensor.Sensor):
	def __init__(self, vehicle, position, rotation):
		sensor.Sensor.__init__(self, vehicle, position, rotation)
		
	def measure(self):
		return 0