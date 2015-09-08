from robot.world import *

class Ultrasonic:
	def __init__(self):
		builder = RobotWorldBuilder()
		builder.buildSensor([0.0, 0.5], pi/2)
		builder.buildSensor([0.0, -0.5], -pi/2)
		builder.buildSensor([0.25, 0], 0)
		builder.buildSensor([-0.25, 0], pi)
		
		builder.buildVehicle(size=(0.5, 1.0), position=[1.0, 0.0], rotation=0.0)
		
		proto = CppResponseGridBlock(128, 8)
		builder.buildGrid(ResponseGrid(4, proto))
		
		self.world = builder.finish()

	def update(self):
		for i, sensor in enumerate(self.world.vehicle.sensors):
			r = sensor.measure()
			
			if r < 4:
				print('Sensor {1}: {0:.3f}'.format(i, r))
				self.world.grid.update(self.world.vehicle.position, sensor.rotation + sensor.vehicle.rotation, r, sensor.angle, False)
			else:
				print('Sensor {1}: {0}'.format(i, '> 4m'))
				self.world.grid.update(self.world.vehicle.position, sensor.rotation + sensor.vehicle.rotation, r, sensor.angle, True)
				
		self.world.update()

def main():
	app = Ultrasonic()
	t = Timer(5.0, app.update)
	t.start()
	
if __name__ == "__main__":
	main()