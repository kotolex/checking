from typing import Any, List
from functools import partial


class Spy:
    """
    The test-double (spy), which replaces the desired object. His attributes return None, and the methods do not do
    anything if unless otherwise indicated, but all of the calls are fixed. This class in used due to make sure in
    the call of respectively functions with arguments.
    """

    def __init__(self, obj: Any = None):
        self.chain: List[Call] = []
        self.returns = {}
        if obj is not None:
            for name in dir(obj):
                if callable(getattr(obj, name)):
                    if name != '__class__':
                        setattr(self, name, partial(self.__function, name))
                    else:
                        setattr(self, name, self.__class__)
                else:
                    setattr(self, name, None)
        self.basic = obj

    def __call__(self, *args, **kwargs):
        self.__function('', *args, **kwargs)
        if '' in self.returns.keys():
            return self.returns['']
        return None

    def __function(self, name, *args, **kwargs):
        self.chain.append(Call(name, *args, **kwargs))
        if name in self.returns:
            return self.returns[name]

    def __str__(self):
        if self.basic is None:
            return f'Empty Test Spy'
        return f'Test spy of the "{self.basic}" {type(self.basic)}'

    def all_calls(self):
        return self.chain

    def was_called(self) -> bool:
        return self.was_function_called('')

    def was_called_with_argument(self, arg: Any) -> bool:
        return self.was_function_with_argument_called('', arg)

    def when_call_returns(self, result: Any):
        self.when_call_function_returns('', result)

    def was_function_called(self, name: str) -> bool:
        return any([e for e in self.chain if e.name == name])

    def was_function_with_argument_called(self, name: str, arg: Any) -> bool:
        if not self.was_function_called(name):
            return False
        return any([e for e in self.chain if e.name == name and arg in e.args])

    def was_exact_function_called(self, name, *args, **kwargs):
        call = Call(name, *args, **kwargs)
        return any([e for e in self.chain if e == call])

    def when_call_function_returns(self, name: str, result: Any):
        self.returns[name] = result


class Call:
    """
    The class which represents a single function call, stores its name and call arguments
    """

    def __init__(self, name: str, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        args = self.args if self.args else 'no args'
        kwargs = self.kwargs if self.kwargs else 'no keyword args'
        return f'Call of "{self.name}" with {args}, {kwargs}'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other is None:
            return False
        if type(other) != type(self):
            return False
        return self.name == other.name and self.args == other.args and self.kwargs == other.kwargs
