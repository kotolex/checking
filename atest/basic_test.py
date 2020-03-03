from typing import Callable

from .test_case import TestCase


class Test(TestCase):

    def __init__(self, name: str, test: Callable):
        super().__init__(name)
        self.test = test
        self.group_name = '__main__'

    def run(self):
        self.test()

    def __str__(self):
        return f'{self.group_name}.{self.test.__name__}'
