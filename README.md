# README #

A simple library to test your python code.

Key Features:



 * no third-party dependencies, only the standard library is used
 * no need to inherit from any classes
 * no need to name your files and/or tests with the prefix or postfix 'test' added
 * it is possible to use native python assert as well as library asserts
 * simple and understandable work with tests, data providers, checks
 * the ability to run based on a file with settings or passing arguments on the command line
 * automatic search for all tests in the current folder and subfolders
 * flexible configuration of both tests and their groups, the ability to group tests and run only selected groups
 * the ability to use both the built-in results processing tool and write your own
 * the ability to group, stop the test by timeout, parallel launch, mocking without installing additional plugins


### Installation ###

Just use your pip

``pip install checking``


### First test ###
Simple example:

```
from checking import *

def my_function_to_test(a,b)
    return a + b

@test
def any_name_you_like():
    # Check  1+1=2
    equals(2, my_function_to_test(1,1))

if __name__ == '__main__':
    # Runs all tests in current module
    start()
```
Only functions marked with the @test annotation are considered tests and will be run, you can name your tests as you wish,
the main thing is to put the @test annotation

## Basic Asserts

You can use simple python assert if you like, but it recommended to use simple and readable library asserts.

###### Standard checks:

```
#!python
@test
def checks_basic_asserts():
    is_true('1', 'Error message') # checks value is True
    is_false([], 'Error message') # checks value is False
    equals(1, 1, 'Error message') # checks two objects are equal (==)
    not_equals(1, 2, 'Error message') # checks two objects are equal (!=)
    is_none(None, 'Error message') # checks object is None
    not_none('1', 'Error message') # checks object is not None
    contains(1, [1, 2, 3], 'Error message') # checks that second argument contains first arg
    not_contains(4, [1, 2, 3], 'Error message') # checks that second argument not contains first arg


```
Messages in all asserts are optional, but it strongly recommended to use them!

###### Work with or without exceptions
If you need to check the exception raises and its message you can write test like:

```
#!python
@test
def check_with_exception():
    with waiting_exception(ZeroDivisionError) as e:
        x = 1 / 0 # Here exception will be raised!
    assert e.message == 'division by zero' # Check message (using python assert)

```
If no exception will be raised or it will be exception of another type - test will fail.
Pay attention - you must check message (if you need to) after exiting context manager, but not inside its scope!

You can't use BaseException here, and it strongly recommended not to use Exception as parent of all exceptions!

In some cases, you need just to run some code and make sure no exception raised. There is a special way for that:

```
#!python
@test
def no_exceptions_bad():
    do_something() # Bad way! No asserts here, is that a test???

@test
def check_no_exception_raises():
    with no_exception_expected(): # Explicitly say that we are not waiting exceptions
        do_something() # Good way!


```
If any exception will be raised - test will fail

###### Managing test during execution

Sometime you need to fail or brake test in execution time on some reason (wrong OS, parameters, etc.)

```
#!python
@test
def must_fail_on_condition():
    if some_condition():
        test_fail('Expected fail!')


@test
def must_be_broken():
    if some_condition():
        test_brake('Expected brake!')

```


### Soft and Fluent Asserts

###### Soft Assert

Soft Assert is a convenient way to checks a few condition before fail. Standard test is preferably fail fast, 
and if some check fails - the test stops. But sometime you need to check a list of conditions, and check them to fail only at the end of the test, 
with all information what checks were failed.
For example you have a json object and want to checks all its fields, but don't want to stop test at first failed check, 
because you want to know what about all other fields!

```
#!python

@test
def check_all_json_fields():
    my_json = get_my_json_somethere()

    soft_assert = SoftAssert() # Creates an object of soft assert
    soft_assert.check(lambda : equals(1, my_json['field1'], 'message')) # Check field, test will not fail here!
    soft_assert.check(lambda : equals('text', my_json['field2'], 'message'))
    soft_assert.contains(1,my_json['list'])
    soft_assert.assert_all() # If something wrong, test will fail here!

```
**Attention!** You always must use assert_all() at the end of the test, only at that moment all exception (if something wrong) 
will be raise.


###### Fluent Assert

Fluent assert is just a sugar to make chains of checks for the object, they are simple, readable, but it is NOT a soft asserts!
If one of the checks will fail - test stops!
Fluent asserts have analogues of the basic asserts, but also have their own types, you can find
them all at checking/classes/fluent_asserts.py

```
#!python

@test
def check_list_valid():
    my_list = get_my_list_somethere()

    verify(my_list).is_not_none().AND.is_a(list).AND.contains(2).AND.is_sorted()

```


## Data Providers

Often you need to run the same test with different data, there is @data annotation for that purposes. Mark any function with @data and
you can use it in your tests. The function for data-provider must not have arguments and it myst returns Iterable, Sequence or generator.

**Important!** Name of the provider have to be unique, you can specify it in parameter @data(name='provider') or it takes the function name by default
It it not necessary to have data-provider with the test (in same module)

Data-provider takes values one by one and push it to your test.
```
#!python
# Create data-provider
@data
def pairs():
    return [(1, 1, 2), (2, 2, 4)]  # Returns list of tuples


@test(data_provider='pairs')  # Specify what provider to use
def check_sum(it):  # Here we must have 1 argument for values of data-provider
    equals(it[0] + it[1], it[2])  # Checks sum of first and second elements of tuple equal to third element

```

## Test Parameters

Test is a function, marked with @test annotation, you can manage them with bunch of parameters:

**enabled** (bool) - if False test will not be run, and all other parameters ignored. By default enabled = True

**name** (str) - name of the test, if not specify the function name will be used

**data_provider** (str) - name of the provider to use with test. If specified, test must have one argument, 
to get values from provider. If no providers found with that name - exception will raise!

**retries** (int) - how many times to run this test if it is failed. If test not fail, no more runs attempted. By default is 1

**groups** (Tuple[str]) - tuple of group names test belongs to, every test is a part of some group, by default group is the module name, where test placed
It is the way to manage and collect tests to any groups.

**priority** (int) - priority of the test, by default is 0. The higher value means test will executes later.
Priority is a way to run tests in some order.

**timeout** (int) - amount of time to wait test ends. If time is over, thread of the test will be interrupted and test will be mark as broken.
Must be use carefully because of potential memory leaks!

**only_if** (Callable[None, bool]) - function, which will be run just before the test, and must returns bool. Test will only be execute if function returns True!
It is a way to make condition for some test, for example run only if OS is Linux.


## Fixtures

Every test, group or all test-suite can have preconditions and post-actions. For example open DB connection before test and close it after.
You can easily make it with before/after fixtures. The function, marked with before/after must be without arguments.

@before  - run function before EACH test in group, by default group is current module, but you can specify it with parameter

@after  - run function after EACH test in group, by default group is current module, but you can specify it with parameter.
This function will not be run if there is @before and it failed!

```
#!python
@before(group_name='api')
def my_func():
    do_some_precondition()

@after(group_name='api')
def another_func():
    do_post_actions()

```

@before_group - function run once before running test in group, by default group is current module, but you can specify it with parameter.

@after_group - function run once after running all test in group, by default group is current module, but you can specify it with parameter. 
This function will not be run if there is @before_group and it failed, except using parameter always_run = True

```
#!python
@before_group(name='api')
def my_func():
    do_some_precondition_for_whole_group()

@after_group(name='api', always_run =True)
def another_func():
    do_post_actions_for_whole_group()

```

@before_suite - function run once before any group at start of the test-suite


@after_suite - function run once after all groups, at the end of the test-suite.
This function will not be run if there is @before_suite and it failed, except using parameter always_run = True

```
#!python
@before_suite
def my_func():
    print('start suite!')

@after_suite(always_run =True)
def another_func():
    print('will be printed, even if before_suite failed!')

```




### Contact me ###
Lexman2@yandex.ru