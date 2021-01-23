from typing import Optional, Dict, Any


class Common:
    """
    Represents a common object that can be used anywhere in tests. For example it can stores some common data, or
    functions to use in tests.
    """

    def __init__(self, params: Optional[Dict] = None):
        self.params = params if params else {}
        self.__dict__ = self.params

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __setitem__(self, item: str, value: Any):
        self.__dict__[item] = value

    def __contains__(self, item: str) -> bool:
        return item in self.__dict__

    def __str__(self):
        return f"Common dictionary: {self.__dict__}"

    def update(self, params: Dict):
        self.__dict__.update(params)

    def clear(self):
        self.__dict__.clear()

    def as_dict(self):
        return dict(self.__dict__)

    def __bool__(self):
        return bool(self.__dict__)
