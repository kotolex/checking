class WrongAnnotationPlacement(Exception):
    """
    Is raised when an incompatible object is decorated:
        - class
        - class method
        - function, which takes arguments when a data provider is not used
        - function, which doesn't take a single argument when a data provider is used
    """
    pass


class DuplicateNameException(Exception):
    """
    Is raised when a data provider name was already registered.
    Rename the data provider function or specify a unique name with the 'name' parameter.
    """
    pass


class UnknownProviderName(Exception):
    """
    Is raised when a data provider with the specified name is not found after the test suite is built.
    """
    pass


class TestBrokenException(Exception):
    """
    Notification, is raised when there is a problem with a test definition,
    a test does not comply with the library API or is marked as "broken" by the user explicitly.
    """
    pass


class TestIgnoredException(Exception):
    """
    Notification, is raised when a test is set up to be ignored by a fixture.
    """
    pass


class OnlyIfFailedException(Exception):
    """
    Notification, is raised when "only_if" predicate on a test case is evaluated to False.
    """
    pass


class SkipTestException(Exception):
    """
    Notification, is raised when user intentionally skips the test by calling test_skip() inside a test.
    """
    pass


class ExceptionWrapper(Exception):
    """
    Wrapper type used with the "should_raise" context manager,
    exposes convenience methods to check for the wrapped exception type and text message.
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
