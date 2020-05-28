# README #

A simple library for testing your own python code.

Key Features:



 * no third-party dependencies, only standard library is used
 * no need to inherit from any classes
 * no need to name your files and/or tests with a prefix or a postfix called 'test'
 * it is possible to interract with native python assert as well as library asserts
 * simple and clear work with tests, data providers, checks, etc.
 * ability to run based on a file with settings or passing arguments on command line
 * automatic search for all tests within a current folder and subfolders
 * flexible configuration of both tests and their groups, the ability to group tests and run only selected groups
 * the ability to use both the built-in results processing tool and write your own one
 * the ability to group, stop test by timeout, parallel launch, mocking without installing extra plugins


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
Only functions marked with @test annotation can be considered as a test and will be ran, you can name your tests whatever you feel like do,
the main point is to put @test annotation

## Basic Asserts

You can manipulate with simple Python assert if you want, but it is recommended to use simple and readable library asserts.

###### Standard checks:

```
#!python
@test
def checks_basic_asserts():
    is_true('1', 'Error message') # checks, if value is True
    is_false([], 'Error message') # checks, if value is False
    equals(1, 1, 'Error message') # checks, if two objects are equal (==)
    not_equals(1, 2, 'Error message') # checks, if two objects are equal (!=)
    is_none(None, 'Error message') # checks, if object is None
    not_none('1', 'Error message') # checks, if object is not None
    contains(1, [1, 2, 3], 'Error message') # checks, if the second argument contains the first arg
    not_contains(4, [1, 2, 3], 'Error message') # checks, if the second argument does not contains the first arg
    is_zero(0, 'Error message') # checks, if argument is equal to 0 (it can be int or float)
    is_positive(1, 'Error message') # checks, if argument is bigger than 0 (for int or float), or len of argument is positive(for Sequence)
    is_negative(-1, 'Error message') # checks, if argument is smaller then 0 (it can be int or float)

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
If no exception will be raised or it will be exception of another type then test will fail.
Pay attention that you should check message (if you need) after exiting context manager, but not inside its scope!

You cannot use BaseException here and it strongly recommended not to use Exception as parent of all exceptions!

In some cases you have just need to run some code and make sure no exception raised. There is a special way for that:

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
If any exception will be raised then test will fail

###### Managing test during execution

Sometimes, you need to fail or brake test in execution time on some reason (wrong OS, parameters, etc.)

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

Soft Assert is a convenient way to check a few conditions before a failure. Standard test is preferably fail fast, 
and if some checks fail then the test stops. But sometimes you need to check a list of conditions, and check them to fail only at the end of the test, 
with all information what checks were failed.
For instance, you have a json object and want to checks all its fields, but also do not want to stop test at first failed check 
because you want to know the state of all other fields!

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
**Attention!** You always should use assert_all() at the end of the test, only at the moment all exception (if something went wrong) 
will be raise.


###### Fluent Assert

Fluent assert is just a sugar to make chains of checks for the object; they are simple, readable, but it is NOT a soft asserts!
If one of the checks will fail - test stops!
Fluent asserts have analogues of the basic asserts, but also have their own types; you can find
them all in checking/classes/fluent_asserts.py

```
#!python

@test
def check_list_valid():
    my_list = get_my_list_somethere()

    verify(my_list).is_not_none().AND.is_a(list).AND.contains(2).AND.is_sorted()

```


## Data Providers

Often you need to run the same test with different data, there is @data annotation for that target. Mark function you want with @data annotation and
you can use it in your tests. The function for data-provider should not have arguments and it has to return iterable, sequence or generator.

**Important!** Name of the provider has to be unique, you can specify it in parameter @data(name='provider') or it takes the function name by default
It it not necessary to have data-provider with the test (in the same module)

Data-provider takes values one by one and pushes it to your test.
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
If you need to use text file as a provider and get data line by line, you can use DATA_FILE function:

```
#!python
from checking import *

# Create data-provider
DATA_FILE('files/data.txt', provider_name='provider') # file at <module folder>/files/data.txt


@test(data_provider='provider')
def try_prov(it):
    print(it)
    is_true(it)
```
In that case file will be read line by line lazily, if no file found - exception will be raised!

If you need all lines be transform in some way, you can use mapping function for that. For example deleting trailing \n
at line end:
```
#!python
from checking import *

# Create data-provider
DATA_FILE('files/data.txt', provider_name='provider', map_function=str.rstrip) # use rstrip() of str to transform


@test(data_provider='provider')
def try_prov(it):
    is_true(it)

```

If you not specify name for data_file, then file_path will be used for it. For example, it is valid use:

```
#!python
from checking import *

# Create data-provider
DATA_FILE('data.txt') # file at module folder, no name for it


@test(data_provider='data.txt') # use file name to find provider
def try_prov(it):
    is_true(it)

```
If you gonna use provider more than once in your test-suite and do not want to get its data from resource of some
kind (database, filesystem, http-request etc.), you can use parameter ``cached=True``. In that case, provider get all 
data only once at first run and stores it in memory for all other tests to run. But make sure you not get too much 
memory for your data and be smart whaen use it in parallel mode. DATA_FILE can use this parameter too.

```#!python
from checking import *

DATA_FILE('data.csv', provider_name='csv', cached=True) # Reads file only once and stores all values


@test(data_provider='csv') # Here comes data from file
def check_one(it):
    not_none(it)


@test(data_provider='csv') # Here comes cached data, no attempts to read file again!
def check_two(it):
    not_none(it)


if __name__ == '__main__':
    start(0)

```

When you need to provide data from simple one-liner like string, list comprehension or generator expression,
you don't need to write function, just use syntactic-sugar CONTAINER

```
#!python
from checking import *

CONTAINER([e for e in range(10)], name='range') # Provide data from list, name is 'range'


@test(data_provider='range')
def try_container(it):
    is_true(it in range(10))

```

If no name specified, the 'container' name will be used. But it is strongly recommended to use unique name here!

```
#!python
from checking import *

CONTAINER((e for e in range(10))) # Provide data from generator


@test(data_provider='container')
def try_container(it):
    is_true(it in range(10))

```

**Important!** You can use DATA_FILE or CONTAINER only at the module global scope, but not at fixtures or tests!

## Test Parameters

Test is a function that marked with @test annotation, you can manage them with bunch of parameters:

**enabled** (bool) - if it is False then test will not be run, and all other parameters ignored. By default enabled = True

**name** (str) - name of the test, if not specify the function name will be used

**description** (str) - test description. If absent, will be taken from function docs. If both description and function
    doc exists, description wins.

**data_provider** (str) - name of the provider to use with test. If specified, test should have one argument, 
to get values from provider. If no providers found with that name then exception will raise!

**retries** (int) - how many times to run the test if it is failed. If test does not fail, no more runs attempted. By defaut it is 1

**groups** (Tuple[str]) - tuple of group names test belongs to, each test is a part of a some group, by default group is the module name, where test places
It is the way to manage and collect tests to any groups.

**priority** (int) - priority of the test, by default it is 0. The higher value means that test will execute later.
Priority is a way to run tests in some order.

**timeout** (int) - amount of time to wait test ends. If time is over, thread of the test will be interrupted and test will be mark as broken.
Should be used carefully because of potential memory leaks!

**only_if** (Callable[None, bool]) - function which will be run before the test, and should return bool. Test will be execute only then if function returns 'True'!
It is a way to make condition for some test, for instance, run only if the OS is Linux.


## Fixtures

Each test group or all test-suite can have preconditions and post-actions. For example, open DB connection before test starts and close it after that.
You can easily make it with before/after fixtures. The function that marked with before/after should be without arguments.

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

@before_suite - function runs once before any group at start of the test-suite


@after_suite - function run once after all groups, at the end of the test-suite.
This function will not be run if there is @before_suite and it failed, except using parameter 'always_run = True'

```
#!python
@before_suite
def my_func():
    print('start suite!')

@after_suite(always_run =True)
def another_func():
    print('will be printed, even if before_suite failed!')

```

## Mock, Double, Stub and Spy

For testing purposes you sometimes need to fake some behaviour or to isolate your application from any other classes/libraries etc.

If you need your test to use fake object, without doing any real calls, yoy can use mocks:


**1. Fake one of the builtin function.**

Let say you need to test function which is using standard input() inside. 

But you cannot wait for real user input during the test, so fake it with mock object.

```
#!python

def our_weird_function_with_input_inside():
    text = input()
    return text.upper()

@test
def mock_builtins_input():
    with mock_builtins('input', lambda : 'test'): # Now input() just returns 'test', it is not to wait for user input
        result_text = our_weird_function_with_input_inside()
        equals('TEST', result_text)
    

```

**2. Fake function of the 3-d party library**

For working with other modules and libraries in test module, you need to import this module and to mock it function.

For example, you need to test function, which is using requests.get inside, but you do not want to make real http
request. Let it mock

some_module_to_test.py
```
#!python
import requests

def func_with_get_inside(url):
    response = requests.get(url)
    return response.text

```

our_tests.py
```
#!python
import requests # need to import it for mock!

from some_module_to_test import func_with_get_inside

@test
def mock_requests_get():
    stub = Stub(text='test') # create simple stub, with attribute text equals to 'test'

    with mock(requests, 'get', lambda x: stub):  # Mock real requests with stub object
        equals('test', func_with_get_inside('https://yandex.ru'))  # Now no real requests be performed!


```

**3. Mock read/write to file**

If you need to mock open function, push data to read from file and gets back with write to file, you can use
mock_open context-manager

```
#!python
def my_open():
    # We read from one file, uppercase results and write to another file
    with open('my_file.txt', encoding='utf-8') as f, open('another.txt', 'wt') as f2:
        f2.write(f.readline().upper())


@test
def mock_open_both():
    # Here we specify what we must "read from file" ('test') and where we want to get all writes(result)
    with mock_open(on_read_text='test') as result:
        my_open()
    equals(['TEST'], result) # checks we get test uppercased

```


**4. Spy object**

Spy is the object which has all attributes of original, but spy not performed any action, 
all methods return None (if not specified what to return). Therefore, spy log all actions and arguments.
It can be useful if your code has inner object and you need to test what functions were called.

```
#!python

def function_with_str_inside(value):
    # Suppose we need to check upper was called here inside
    return value.upper()

@test
def spy_for_str():
    spy = Spy('it is a string') # Spy, which is like str, but it is not str!
    function_with_str_inside(spy) # Send our spy instead a str
    is_true(spy.upper.was_called()) # Verify upper was called
    

```

You can even specify what to return when some function of the spy will be called!

```
#!python

def function_with_str_inside(value):
    # Suppose we need to check upper was called here inside
    return value.upper()


@test
def spy_with_return():
    spy = Spy('string')
    spy.upper.returns('test') # Tells what to return, when upper will be call
    result = function_with_str_inside(spy)
    is_true(spy.upper.was_called())
    equals('test', result) # verify our spy returns 'test'

```

Spy object can be created without original inner object and can be call itself, it can be useful when you need
some dumb object to know it was called.
```
#!python
@test
def check_spy():
    spy = Spy()  # Create "empty" spy
    spy()  # Call it
    is_true(spy.was_called())  # Checks spy was called

```

**5. Double object**

Double object is like the Spy, but it saves original object behaviour, so its methods returns 
real object methods results if not specified otherwise.

```
#!python
@test
def check_double():
    spy = Double("string")  # Create str double-object
    equals(6, len(spy))  # Len returns 6 - the real length of original object ("string")
    spy.len.returns(100)  # Fake len result
    equals(100, len(spy))  # Len now returns 100

```

**6. Stub object**

Stub object is just a helper for testing, its purpose not to check or assert something, but to give data
and perform some simple action, when application under test need it. Unlike spy or double, Stub 
is not remember calls, it just a simple replacement for some object with minimum or no logic inside.

Lets say we have a function which gets some object, take its attribute, calculates something and 
return result. We wish to isolate our testing from real objects, just test important behaviour, besides 
this data-object can be hard to create or complicated.
```
#!python
from checking import *

# Our function to test, it get some object and use it attribute and method, but we just 
# need to test how it works!
def function(some_object)->int:
    initial_value = some_object.value
    result = 2 + some_object.complicate_function()*initial_value  # Some calculation we need to test
    return result


@test
def check_with_stub():
    stub = Stub(value=2) # Creates stub with attribute value=2
    stub.complicate_function.returns(2) # Says, when complicate_function will be called returns 2
    equals(6, function(stub))  # Asserts 6 == 2+(2*2)

```
Pay attention - when you look for some attribute in stub - it always has it! But it will be a wrapper to use with 
expression like `stub.any_attribute.returns('test')`. 

So, if you need to have some attribute (not method) on stub, you just use `stub.attr=10`, but for methods just use expression above.


### Command Line Options ###

You can run all your tests in current folder and all sub-folders with your terminal:

```commandline
python -m checking
```
There are few parameters for run in terminal:

**-o options.json**  tells to look at the file options.json for test-suite parameters. 
If specified, **-d** and **-f** options will be ignored!

**-g** just generates default .json file for your options! If specified, all other options will be ignored!

**-a arg** or **-a key=value**   add argument to common parameters of the suite to use later at tests

**-d**    dry-run mode, no real tests will be executed, just collects and counts.

**-f name**    filters test name, only test whose name contains filter will be executed

**-r**    runs all tests in random order (priority will be ignored)


### Options File Parameters ###

Options file is a way to manage your suite(s), you can have a few of them with different names to use in any case you 
need, for example 1 file for run all tests, another to run only api tests etc. 
File must have .json extension and contains valid json.
For your convenience you can generate one with
```commandline
python -m checking -g
```
In current working folder a file will appear with content like:
```json
{"suite_name": "Default Test Suite", 
"verbose": 0, 
"groups": [], 
"params": {}, 
"listener": "", 
"modules": [], 
"threads": 1, 
"dry_run": false, 
"filter_by_name": "",
"random_order": false}
```
Changing this parameters you can manage your suites and test  - for example specify what listener to use, or what group to run only.
Some rules for parameters:

1) All types must be as in example, so you cant put string to "verbose" it must be int, etc.

2) If groups not empty ("groups":["api"]) then only group with that name will run. If no such group found, no tests will executed

3) Listener must be specified with module, like "listener": "my_module.MyListener". It is not necessary
to specify whole path, just module name and class name. If not specified, default listener will be used. You can use
default listener names here, like "listener":"DefaultFileListener"

4) Modules must be specified without ".py"! If modules parameter is empty than all found modules with tests will be imported.
If modules specified("modules":["my_package.my_module"]) only that modules be imported, and tests wil be collected from it. 
You can specify just module names or package.module (no need to specify full path)




### Contact me ###
Lexman2@yandex.ru