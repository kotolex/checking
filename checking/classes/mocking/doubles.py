from typing import Any, List, Tuple

from .calls import Call
from .interfaces import Observer
from .wrapper import AttributeWrapper


class Spy(Observer):
    """
    The test-double (spy), which replaces the desired object. His attributes return None, and the methods do not do
    anything if unless otherwise indicated, but all of the calls are fixed. This class in used due to make sure in
    the call of respectively functions with arguments.
    """

    def __init__(self, obj: Any = None):
        super().__init__()
        self.chain: List[Call] = []
        self._returns = None
        if obj is not None:
            for name in dir(obj):
                if callable(getattr(obj, name)):
                    if name != '__class__':
                        setattr(self, name, AttributeWrapper(name, self))
                    else:
                        setattr(self, name, self.__class__)
                else:
                    setattr(self, name, None)
        self.basic = obj

    def notify(self, _call: Call):
        self.chain.append(_call)

    def __call__(self, *args, **kwargs):
        self.chain.append(Call('', *args, **kwargs))
        return self._returns

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

    def returns(self, result: Any):
        """
        If spy object will be called itself return result
        :param result: any type to return when call
        :return: None
        """
        self._returns = result

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
                attr = getattr(obj, name)
                if callable(attr):
                    if name != '__class__':
                        wrapper = AttributeWrapper(name, self)
                        wrapper.use_function(attr)
                        setattr(self, name, wrapper)
                    else:
                        setattr(self, name, self.__class__)
                else:
                    setattr(self, name, attr)
        wrapper = AttributeWrapper('len', self)
        setattr(self, 'len', wrapper)
        wrapper = AttributeWrapper('bool', self)
        setattr(self, 'bool', wrapper)
        wrapper = AttributeWrapper('iter', self)
        setattr(self, 'iter', wrapper)
        self.basic = obj

    def __str__(self):
        return f'Test Double of the "{self.basic}" {type(self.basic)}'

    def __len__(self):
        if self.len._return is not None or self.len._function:
            return self.len()
        self.len()
        return len(self.basic)

    def __bool__(self):
        if self.bool._return is not None or self.bool._function:
            return self.bool()
        self.bool()
        return bool(self.basic)

    def __iter__(self):
        if self.iter._return is not None or self.iter._function:
            return self.iter()
        self.iter()
        return iter(self.basic)
