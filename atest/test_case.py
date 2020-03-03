from typing import List, Callable


class TestCase:
    def __init__(self, name: str):
        self.name = name
        self.before: List[Callable] = []
        self.after: List[Callable] = []
        self.is_before_failed: bool = False
        self.always_run_after: bool = False

    def add_before(self, func: Callable):
        self.before.append(func)

    def add_after(self, func: Callable):
        self.after.append(func)
