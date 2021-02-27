class Simulator:
    def __init__(self, speed):
        self.speed = speed

    def is_simulator(self):
        return self.speed is not None
