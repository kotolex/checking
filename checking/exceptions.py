class WrongAnnotationPlacement(Exception):
    """
    It throws if the annotation is set over a function that takes arguments, or over a class/class method. When using
    the @test annotation with the data provider, it will be thrown if the function does not accept at least one
    argument.
    """
    pass


class DuplicateNameException(Exception):
    """
    It will be thrown if the provider name is already in the set, you need to rename the data provider method or give
    it a name through the parameter.
    """
    pass


class UnknownProviderName(Exception):
    """
    It will be thrown if, after the formation of the test run (test-suite), the provider with the specified name is not
    found.
    """
    pass


class TestBrokenException(Exception):
    """
    It will be thrown to notify of problems with the test, not related to assert.
    """
    pass


class TestIgnoredException(Exception):
    """
    It will be thrown to notify that the test is ignored (fixtures failed or only_if).
    """
    pass


class ExceptionWrapper(Exception):
    """
    The wrapper for exceptions to which you can then pass another exception. Used with waiting_exception.
    """

    def __init__(self):
        self.value = None
        self.message = 'Expect exception, but none raised!'
        self.args = (self.message,)
        self.type = type(self)

    def __str__(self):
        return str(self.value) if self.value else self.message

    def set_value(self, exception: Exception):
        self.value = exception
        self.args = exception.args
        self.message = self.args[0]
        self.type = type(exception)
