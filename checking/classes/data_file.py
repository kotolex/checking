from typing import Callable


class DataFile:
    """
    Wrapper for open text file, can change line on reading with function. Used for data-provider.
    """

    def __init__(self, file_name: str, encoding: str = 'UTF-8', map_function: Callable = None):
        self.file = open(file_name, encoding=encoding)
        self.map_ = map_function if map_function else lambda line: line

    def __iter__(self):
        return (self.map_(line) for line in self.file)

    def close(self):
        self.file.close()
