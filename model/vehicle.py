
class Vehicle:
    """
        Движущаяся платформа с датчиками
    """
    def __init__(self, size, position, rotation, world):
        self.width, self.height = size

        self.position = position
        self.rotation = rotation
        self.sensors = []

        self.world = world