from typing import Callable, Any, Optional

from .timer import Timer
from .basic_case import TestCase
from ..exceptions import TestIgnoredException


class Test(TestCase):
    """
    The class which representing test, the main point of test run.
    """
    __slots__ = ('name', 'before', 'after', 'is_before_failed', 'always_run_after', 'provider', 'retries', 'priority',
                 'test', 'group', 'group_name', 'argument', 'timeout', 'only_if', 'description', 'timer', 'status',
                 'reason')

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
        self.group = None
        # Argument for data-provider run
        self.argument: Any = None
        # Time in seconds to finish test
        self.timeout: int = 0
        # Function-predicate, if return False - test will not runs
        self.only_if: Optional[Callable] = None
        # Description of the test
        self.description = test.__doc__
        # The name of the provider for future delivery of data to the test
        self.provider = None
        # The number of the test run attempts
        self.retries: int = 1
        # Test priority where 0 is highest
        self.priority: int = 0
        # Timer for start, end and duration parameters of the test
        self.timer = Timer()
        # Status of the test
        self.status: str = 'created'
        # Raised exception
        self.reason: Optional[Exception] = None

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
        self.timer.start()
        if self.argument is not None:
            self.test(self.argument)
        else:
            self.test()

    def stop(self, exception_: Optional[BaseException] = None):
        """
        Stop the test - just get the time and save status and exception. After that put test to results of the group.
        :param exception_: If None, then test is succeed.
        :return: None
        """
        self._stop()
        self.reason = exception_
        if not exception_:
            self.status = 'success'
        elif type(exception_) in (TestIgnoredException, SystemExit):
            self.status = 'ignored'
            self.timer.start_time = -1
            self.timer._end_time = -1
            self.timer.duration = 0
        elif type(exception_) is AssertionError:
            self.status = 'failed'
        else:
            self.status = 'broken'
        self._put_to_group_results()

    def _stop(self):
        """
        Save end time and calculate duration of the test
        :return: None
        """
        self.timer.stop()

    def _put_to_group_results(self):
        if self.group:
            self.group.add_result(self)

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
        for attr in self.__slots__:
            setattr(clone, attr, getattr(self, attr))
        return clone

    def duration(self) -> float:
        return self.timer.duration

    def info(self) -> dict:
        """
        Statistics of the test
        :return: dict of main parameters
        """
        return {'group': self.group_name, 'name': self.name, 'description': self.description, 'priority': self.priority,
                'argument': self.argument, 'timeout': self.timeout, 'retries': self.retries, 'status': self.status,
                'reason': self.reason, 'duration': self.duration()}
