from random import shuffle
from typing import List, Callable

from .basic_test import Test
from .basic_case import TestCase


class TestGroup(TestCase):
    """
    The test set or group of tests is all tests from one module, or all tests are contained from one group, but it is
    not a test-suite (the set of all sets). Test-suite might be only one and contains all sets of tests, a test-suite is
    used to creating during testing starts. If there is at least 1 test, then a test set will be created and placed
    in a test-suite, during start.
    """

    __slots__ = ('name', 'before', 'after', 'is_before_failed', 'always_run_after', 'tests', 'before_all', 'after_all',
                 'test_results')

    def __init__(self, name: str):
        super().__init__(name)
        # The list of tests, i.e instances of 'Test' class
        self.tests: List[Test] = []
        # The list of functions that executed before each test
        self.before_all: List[Callable] = []
        # The list of functions that executed after each test
        self.after_all: List[Callable] = []
        # The list of the results of the run of this set
        self.test_results: List[Test] = []

    def add_test(self, test: Test):
        """
        Adding the test in the set, wherein receives the name of the group, lists of preliminaries and subsequents
        functions.
        :param test: is the instance of 'Test' class
        :return: None
        """
        test.set_group(self)
        test.before = self.before_all
        test.after = self.after_all
        self.tests.append(test)

    def add_before_test(self, func: Callable):
        """
        Adding one more function in preliminary pull, for executing before each test.
        :param func: is the function
        :return: None
        """
        self.before_all.append(func)

    def add_after_test(self, func: Callable):
        """
        Adding one more function in final pull, for executing after each test.
        :param func: is the function
        :return: None
        """
        self.after_all.append(func)

    def add_result(self, test: Test):
        """
        Adding the test in appropriate section of the results dictionary.
        :param test: is the instance of the TestCase
        :return: None
        """
        self.test_results.append(test)

    def is_empty(self):
        """
        Checking, if the set is empty.
        :return: True, if there are no tests inside the set
        """
        return len(self.tests) == 0

    def tests_count(self):
        """
        Returns the number of tests. If tests have been executed and there are results, it returns the sum of tests from
        results, otherwise it returns the number of 'TestCase; within 'tests' list. It has done due to at the time of
        starting the tests it is not know how many of them will be in total, thanks to restarts (retries) and/or to
        providers.
        :return: the number of the tests
        """
        return len(self.test_results) if self.test_results else len(self.tests)

    def sort_test_by_priority(self):
        self.tests = sorted(self.tests, key=lambda t: t.priority)

    def shuffle_tests(self):
        """
        Change test order randomly, ignoring priority
        :return: None
        """
        shuffle(self.tests)

    def tests_by_status(self, status: str) -> List[Test]:
        return [test for test in self.test_results if test.status == status]
