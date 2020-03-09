from atest import *


@test
def first():
    assert 1 == 2


@test(name='one_not_two')
def second():
    equals(1, 2, "cant be")


@test
def third():
    1 / 0


@test
def fourth():
    is_none(None)



class Cat:

    def some(self):
        pass


if __name__ == '__main__':
    start(verbose=3)
