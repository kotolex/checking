from typing import Callable, Any

from .basic_case import TestCase
from ..exceptions import TestIgnoredException


class Test(TestCase):
    """
    The class which representing test, the main point of test run.
    """
    __slots__ = ('name', 'before', 'after', 'is_before_failed', 'always_run_after', 'provider', 'retries', 'priority',
                 'test', 'group', 'group_name', 'argument', 'timeout', 'only_if', 'description')

    def __init__(self, name: str, test: Callable):
        """
        Object initialization requires not only name, but a function reference, which is a test.
        :param name: is the name of the test
        :param test: is the function that will be launch at the test executes
        """
        super().__init__(name)
        # Function to run (the test itself)
        self.test = test
        self.group_name: str = '__main__'
        self.group= None
        # Argument for data-provider run
        self.argument: Any = None
        # Time in seconds to finish test
        self.timeout: int = 0
        # Function-predicate, if return False - test will not runs
        self.only_if: Callable = None
        # Description of the test
        self.description = test.__doc__
        # The name of the provider for future delivery of data to the test
        self.provider = None
        # The number of the test run attempts
        self.retries: int = 1
        # Test priority where 0 is highest
        self.priority: int = 0

    def set_group(self, group):
        self.group = group
        self.group_name = group.name

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
            description = description.replace('\n', '').replace('  ', '')
            description = f" ('{description}')"
        return f'{self.group_name}.{self.name}{description}'

    def clone(self):
        """
        Cloning the instance
        :return: a new Test
        """
        clone = Test(self.name, self.test)
        clone.group = self.group
        clone.group_name = self.group_name
        clone.provider = self.provider
        clone.after = self.after
        clone.before = self.before
        clone.is_before_failed = self.is_before_failed
        clone.always_run_after = self.always_run_after
        clone.retries = self.retries
        clone.priority = self.priority
        clone.argument = self.argument
        clone.timeout = self.timeout
        clone.only_if = self.only_if
        clone.description = self.description
        return clone
