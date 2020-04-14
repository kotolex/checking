from typing import Callable, Any

from .basic_case import TestCase
from ..exceptions import TestIgnoredException


class Test(TestCase):
    """
    The class which representing test, the main point of test run.
    """

    def __init__(self, name: str, test: Callable):
        """
        Object initialization requires not only name, but a function reference, which is a test.
        :param name: is the name of the test
        :param test: is the function that will be launch at the test executes
        """
        super().__init__(name)
        self.test = test
        self.group_name: str = '__main__'
        self.argument: Any = None
        self.timeout: int = 0
        self.only_if: Callable = None
        self.description = test.__doc__

    def run(self):
        """
        The launch of the test (functions mark tests annotation).
        :return: None
        """
        if self.only_if:
            if not self.only_if():
                raise TestIgnoredException()
        if self.argument is not None:
            self.test(self.argument)
        else:
            self.test()

    def __str__(self):
        description = self.description if self.description else ''
        if description:
            description = description.replace('\n','').replace('  ', '')
            description = f"('{description}')"
        return f'{self.group_name}.{self.name} {description}'

    def clone(self) -> TestCase:
        """
        Cloning the instance and mutable fields are also coping.
        :return: a new Test
        """
        clone = Test(self.name, self.test)
        clone.group_name = self.group_name
        clone.provider = self.provider
        clone.after = self.after[:]
        clone.before = self.before[:]
        clone.is_before_failed = self.is_before_failed
        clone.always_run_after = self.always_run_after
        clone.retries = self.retries
        clone.priority = self.priority
        clone.argument = self.argument
        clone.timeout = self.timeout
        clone.only_if = self.only_if
        clone.description = self.description
        return clone
