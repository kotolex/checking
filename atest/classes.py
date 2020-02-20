from typing import Callable
from collections import defaultdict


class Test:
    before = defaultdict(list)
    before_was_successful = False
    after = defaultdict(list)
    before_test = defaultdict(list)
    after_test = defaultdict(list)
    counter = 0

    def __init__(self, module_name: str, test: Callable):
        self.module_name = module_name
        self.test = test
        Test.counter += 1

    def __str__(self):
        return f'{self.module_name}.{self.test.__name__}'

    def __run_from_dict(self, a_dict: defaultdict):
        if self.module_name in a_dict:
            for element in a_dict[self.module_name]:
                element()
            if a_dict is Test.before or a_dict is Test.after:
                del a_dict[self.module_name]
                Test.before_was_successful = True

    def run(self):
        Test.counter -= 1
        self.__run_from_dict(Test.before)
        self.__run_from_dict(Test.before_test)
        self.test()
        self.__run_from_dict(Test.after_test)
        self.finish()

    def finish(self):
        if Test.counter == 0 and Test.before_was_successful:
            Test.counter = -1
            self.__run_from_dict(Test.after)

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
