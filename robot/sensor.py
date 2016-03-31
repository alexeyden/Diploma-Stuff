from model import sensor
from model.util import *

import random

class RobotSensor(sensor.Sensor):
    def __init__(self, vehicle, position, rotation, port, name=None):
        sensor.Sensor.__init__(self, vehicle, position, rotation, name)

        self.port = port
        self.angle = to_rad(30)

    def measure(self):
        '''with serial.Serial(port=self.port, timeout=0.05) as ss:
            ss.readall()
            ss.write(b'')
            data = ss.readall()
            self.lastRange = rng / 128.0 / 58.0 / 100.0
        '''
        self.lastRange = random.uniform(0.5, 3)
        return self.lastRange
