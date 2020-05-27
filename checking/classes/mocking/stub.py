from .interfaces import Observer
from .wrapper import AttributeWrapper


class Stub(Observer):
    """
    Stub is a test-double which main purpose is to give some data to application under test in cases when it need data
    to work and test properly. It is not for checking or assertions, just for separate application from data source.
    """
    def __init__(self, **kwargs):
        """
        You can mention all attributes here in key-value pairs. If you need to specify method or function use
        stub.method.returns(None) instead
        :param kwargs: key-value pairs for fill attributes of object
        """
        super().__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, item):
        if item not in self.__dict__:
            self.__dict__[item] = AttributeWrapper(item, self)
        return self.__dict__[item]

    def __str__(self):
        return f'Stub object {self.__dict__}'

    def notify(self, call_):
        pass
