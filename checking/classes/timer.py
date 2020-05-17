from time import time


class Timer:
    """
    Simple class for checking time
    """

    def __init__(self):
        self.start_time: float = -1
        self.end_time: float = -1
        self.duration: float = -1

    def start(self):
        self.start_time = time()

    def stop(self):
        self.end_time = time()
        self.duration = self.end_time - self.start_time

    def reset(self):
        self.start_time = -1
        self.end_time = -1
        self.duration = -1
