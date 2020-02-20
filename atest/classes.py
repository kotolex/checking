from typing import Callable
from collections import defaultdict


class Test:
    before = defaultdict(list)
    after = defaultdict(list)

    def __init__(self, module_name: str, test: Callable):
        self.module_name = module_name
        self.test = test
        self.before_me = None
        self.after_me = None

    def run(self):
        if self.before_me:
            self.before_me()
        self.test()
        if self.after_me:
            self.after_me()

    @classmethod
    def before_module(cls, module_name: str, function: Callable):
        cls.before[module_name].append(function)

    @classmethod
    def after_module(cls, module_name: str, function: Callable):
        cls.after[module_name].append(function)
