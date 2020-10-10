from typing import List, Callable


class TestCase:
    """
    Parent for test and group of tests (test set) has the common methods.
    """
    __slots__ = ('name', 'before', 'after', 'is_before_failed', 'always_run_after')

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

    def add_before(self, func: Callable):
        self.before.append(func)

    def add_after(self, func: Callable):
        self.after.append(func)
