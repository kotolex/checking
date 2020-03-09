from atest import *


@test(priority=1)
def first():
    assert common_parameters['selenium'] == 'sel'


@test(name='one_not_two', priority=2)
def second():
    equals(1, 1, "cant be")


@test(groups=['a', 'b'])
def third():

    assert 2 == 2


@test
def fourth():
    common_parameters['selenium'] = 'sel'
    is_none(None)


class Cat:

    def some(self):
        pass


if __name__ == '__main__':
    start(verbose=3)
