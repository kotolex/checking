from atest import *


@test(priority=1)
def first():
    assert 1 == 1


@test(name='one_not_two', priority=2)
def second():
    equals(1, 1, "cant be")


@test
def third():
    assert 2 == 2


@test
def fourth():
    is_none(None)


class Cat:

    def some(self):
        pass


if __name__ == '__main__':
    start(verbose=3)
