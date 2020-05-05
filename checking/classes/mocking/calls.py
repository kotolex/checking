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
