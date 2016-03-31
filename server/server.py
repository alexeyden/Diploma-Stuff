from http.server import HTTPServer
from .handler import RequestHandler
from .ultrasonic import Ultrasonic, RangefinderUpdateThread
from robot.world import RobotWorldBuilder
import math


class Server(HTTPServer):
    def __init__(self, host, port):
        super().__init__((host, port), RequestHandler)

        builder = RobotWorldBuilder()
        builder.port = '/dev/ttyUSB0'

        builder.buildSensor([0.0, 0.5], math.pi/2, 'front')

        self.update_thread = RangefinderUpdateThread(1, Ultrasonic(builder))

    def run(self):
        try:
            self.update_thread.start()
            self.serve_forever()
        except KeyboardInterrupt:
            self.update_thread.done.set()
            self.socket.close()
