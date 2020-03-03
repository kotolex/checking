from typing import List, Callable, Dict

from .basic_test import Test
from .test_case import TestCase


class TestGroup(TestCase):

    def __init__(self, name: str):
        super().__init__(name)
        self.tests: List[Test] = []
        self.before_all: List[Callable] = []
        self.after_all: List[Callable] = []
        self.test_results: Dict[str, List[Test]] = {'success': [], 'broken': [], 'failed': [], 'ignored': []}

    def add_test(self, test: Test):
        test.group_name = self.name
        for before in self.before_all:
            test.add_before(before)
        for after in self.after_all:
            test.add_after(after)
        self.tests.append(test)

    def add_before_test(self, func: Callable):
        self.before_all.append(func)
        for test in self.tests:
            test.add_before(func)

    def add_after_test(self, func: Callable):
        self.after_all.append(func)
        for test in self.tests:
            test.add_after(func)

    def add_result_to(self, test: Test, result: str = 'success'):
        self.test_results[result].append(test)

    def is_empty(self):
        return len(self.tests) == 0
