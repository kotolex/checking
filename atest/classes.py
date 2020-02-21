from typing import Callable
from collections import defaultdict


class Test:
    before = defaultdict(list)
    after = defaultdict(list)
    before_test = defaultdict(list)
    after_test = defaultdict(list)
    counter = defaultdict(int)

    def __init__(self, module_name: str, test: Callable):
        self.module_name = module_name
        self.test = test
        self.run_after_module_always = False
        Test.counter[self.module_name] += 1

    def __str__(self):
        return f'{self.module_name}.{self.test.__name__}'

    def __run_from_dict(self, a_dict: defaultdict):
        if self.module_name in a_dict:
            for element in a_dict[self.module_name]:
                element()
            if a_dict is Test.before or a_dict is Test.after:
                del a_dict[self.module_name]

    def run_before_module(self):
        self.__run_from_dict(Test.before)

    def run_before_test(self):
        self.__run_from_dict(Test.before_test)

    def run(self):
        self.test()

    def run_after_test(self):
        self.__run_from_dict(Test.after_test)

    def run_after_module(self):
        if Test.counter[self.module_name] == 0 and (Test.before_module or self.run_after_module_always):
            Test.counter = -1
            self.__run_from_dict(Test.after)

    def count_down(self):
        Test.counter[self.module_name] -= 1

    @classmethod
    def before_module(cls, module_name: str, function: Callable):
        cls.before[module_name].append(function)

    @classmethod
    def after_module(cls, module_name: str, function: Callable):
        cls.after[module_name].append(function)

    @classmethod
    def before_each(cls, module_name: str, function: Callable):
        cls.before_test[module_name].append(function)

    @classmethod
    def after_each(cls, module_name: str, function: Callable):
        cls.after_test[module_name].append(function)
