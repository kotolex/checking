from typing import Dict, List, Callable

from .test_group import TestGroup
from .basic_test import Test


class TestSuite:
    instance = None
    groups: Dict[str, TestGroup] = {}
    before: List[Callable] = []
    after: List[Callable] = []
    name: str = 'Default Test Suite'
    is_before_failed: bool = False
    always_run_after: bool = False

    def __new__(cls, *args, **kwargs):
        if not TestSuite.instance:
            TestSuite.instance = super(TestSuite, cls).__new__(cls)
        return TestSuite.instance

    @classmethod
    def add_before(cls, func: Callable):
        cls.before.append(func)

    @classmethod
    def add_after(cls, func: Callable):
        cls.after.append(func)

    @classmethod
    def get_instance(cls):
        return TestSuite()

    @classmethod
    def get_or_create(cls, group_name: str) -> TestGroup:
        if group_name not in cls.groups:
            cls.groups[group_name] = TestGroup(group_name)
        return cls.groups[group_name]

    @classmethod
    def is_empty(cls) -> bool:
        return all([group.is_empty() for group in cls.groups.values()])

    @classmethod
    def tests_count(cls) -> int:
        if cls.is_empty():
            return 0
        return sum([len(group.tests) for group in cls.groups.values()])

    @classmethod
    def failed(cls) -> List[Test]:
        return [test for group in cls.groups.values() for test in group.test_results['failed']]

    @classmethod
    def broken(cls) -> List[Test]:
        return [test for group in cls.groups.values() for test in group.test_results['broken']]

    @classmethod
    def ignored(cls) -> List[Test]:
        return [test for group in cls.groups.values() for test in group.test_results['ignored']]
