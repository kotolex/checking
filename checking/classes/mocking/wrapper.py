from typing import Any, List, Callable

from .calls import Call
from .interfaces import Observer


class AttributeWrapper:
    """
    Wrapper for all methods of mocked object. Use it to change behaviour, returns something or raise exception
    on method calls.
    """

    def __init__(self, name: str, observer: Observer):
        self.name = name
        self._function = None
        self._return = None
        self._raise = None
        self._raise_condition = None
        self._calls = []
        self.observer = observer

    def __str__(self):
        return f'Wrapper for method "{self.name}" on object: {self.observer}"'

    def returns(self, arg: Any):
        """
        Specify what to return on object method call
        :param arg: any object
        :return: None
        """
        self._return = arg
        self._function = None

    def raises(self, exception: Exception, message: str = None):
        """
        Raises this exception on method call
        :param exception: Exception or its children
        :param message: Message for exception
        :return: None
        """
        self._raise = (exception, message)
        self._raise_condition = None

    def raises_if_args(self, predicate: Callable[[Any], bool], exception: Exception, message: str = None):
        """
        Raises this exception on method call, if predicate returns True on call arguments. If method will be call
        without arguments - no checks will be performed, and no exception raise.
        :param predicate: function to check call arguments
        :param exception: Exception to raise
        :param message: additional message
        :return: None
        """
        self._raise = (exception, message)
        self._raise_condition = predicate

    def __call__(self, *args, **kwargs):
        self._calls.append((args, kwargs))
        self.observer.notify(Call(self.name, *args, **kwargs))
        if self._raise:
            exception, message = self._raise
            if self._raise_condition and (args or kwargs):
                if self._raise_condition(*args, **kwargs):
                    raise exception(message)
            elif not self._raise_condition:
                raise exception(message)
        if self._function:
            return self._function(*args, **kwargs)
        return self._return

    def use_function(self, function: Callable):
        """
        Will call specified function on method call
        :param function: function to call
        :return: None
        """
        self._function = function

    def was_called(self) -> bool:
        return len(self._calls) > 0

    def call_count(self) -> int:
        return len(self._calls)

    def all_calls(self) -> List:
        return self._calls
