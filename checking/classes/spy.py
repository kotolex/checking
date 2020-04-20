from typing import Any, List, Tuple
from functools import partial


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

    def all_calls(self) -> List[Call]:
        """
        Returns list of Call objects (all method calls of the spied object)
        :return: List[Call]
        """
        return self.chain

    def was_called(self) -> bool:
        """
        Returns True if spy object was called itself
        :return: bool
        """
        return self.was_function_called('')

    def was_called_with_argument(self, arg: Any) -> bool:
        """
        Returns True if spy object was called itself with exact argument
        :param arg: Any argument to look for
        :return: bool
        """
        return self.was_function_with_argument_called('', arg)

    def when_call_returns(self, result: Any):
        """
        If spy object will be called itself return result
        :param result: any type to return when call
        :return: None
        """
        self.when_call_function_returns('', result)

    def was_function_called(self, name: str) -> bool:
        """
        Returns True if exact function/method was called on spied object
        :param name: name of the function/method
        :return: bool
        """
        return any([e for e in self.chain if e.name == name])

    def was_function_with_argument_called(self, name: str, arg: Any) -> bool:
        """
        Returns True if exact function/method was called with exact argument on spied object
        :param name: name of the function/method
        :param arg: any argument
        :return: bool
        """
        if not self.was_function_called(name):
            return False
        return any([e for e in self.chain if e.name == name and arg in e.args])

    def was_exact_function_called(self, name, *args, **kwargs):
        call = Call(name, *args, **kwargs)
        return any([e for e in self.chain if e == call])

    def when_call_function_returns(self, name: str, result: Any):
        """
        Replace result of the function/method call with some new result
        :param name: name of the function
        :param result: any result to return
        :return: None
        """
        self.returns[name] = result

    def all_calls_args(self) -> List[Tuple]:
        """
        Returns all called function/method arguments
        :return: List[Tuple]
        """
        return [e.args for e in self.chain]

    def all_calls_args_flatten(self) -> List[Any]:
        """
        Returns flat list of all arguments of all called functions
        :return: List[Any]
        """
        return [arg for call in self.chain for arg in call.args]


class Double(Spy):
    """
        The full test-double (twin of the object), the main difference with Spy is behaviour. Behaviour stays the same
        as original object has, but all calls fixed and you can change return result of the methods.
        This class in used due to make sure in the call of respectively functions with arguments.
    """

    def __init__(self, obj: Any = None):
        super().__init__()
        if obj is not None:
            for name in dir(obj):
                if callable(getattr(obj, name)):
                    if name != '__class__':
                        setattr(self, name, partial(self.__function, name))
                    else:
                        setattr(self, name, self.__class__)
        self.basic = obj

    def __function(self, name, *args, **kwargs):
        self.chain.append(Call(name, *args, **kwargs))
        if name in self.returns:
            return self.returns[name]
        else:
            return getattr(self.basic, name)(*args, **kwargs)

    def __str__(self):
        return f'Test Double of the "{self.basic}" {type(self.basic)}'

    def __len__(self):
        return len(self.basic) if '__len__' not in self.returns else self.returns['__len__']

    def __bool__(self):
        return bool(self.basic) if '__bool__' not in self.returns else self.returns['__bool__']

    def __iter__(self):
        return iter(self.basic) if '__iter__' not in self.returns else self.returns['__iter__']
