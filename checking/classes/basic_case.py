from typing import List, Callable


class TestCase:
    """
    Parent for test and group of tests (test set) has the common methods.
    """

    def __init__(self, name: str):
        self.name = name
        # The list of the functions that execute before test/group
        self.before: List[Callable] = []
        # The list of the functions that execute after test/group
        self.after: List[Callable] = []
        # The flag that the preliminary operation has fallen, in this case the function will not start after the test
        self.is_before_failed: bool = False
        # The flag of obligatory start of function after the test, even if the preliminary ones has fell down
        self.always_run_after: bool = False
        # The name of the provider for future delivery of data to the test
        self.provider = None
        # The number of the test run attempts
        self.retries: int = 1
        # Test priority where 0 is highest
        self.priority: int = 0

    def add_before(self, func: Callable):
        self.before.append(func)

    def add_after(self, func: Callable):
        self.after.append(func)