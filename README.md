# README #

A simple testing library for your python code.

Key features:

 * no third-party dependencies
 * no need to inherit from any classes
 * no need to name your files and/or tests with a "test" prefix/postfix
 * interaction with native python asserts as well as library-provided asserts
 * simple and clean workflow with test cases, data providers, asserts, etc.
 * run mode configuration via a config file or command line parameters
 * automatic recursive test discovery for the current directory tree
 * test groups, group-vise test execution, flexible configuration for both tests and test groups 
 * result processing middleware, both built-in and user-defined
 * flexible test execution mode configuration: timeouts, parallel execution, etc.
 * mocks with no third-party dependencies or extra plug-ins
 * configurable HTML report generator

### Installation ###

Via pip:

``pip install checking``

### First test ###

```
from checking import *

def my_function_to_test(a,b):
    return a + b

@test
def any_name_you_like():
    # assert 1+1=2
    equals(2, my_function_to_test(1,1))

if __name__ == '__main__':
    # runs all tests in current module
    start()
```

Only functions marked with @test decorator will be marked as tests to execute. 
You can name your tests however you like, just put that @test decorator.

### Basic Asserts ###

You can use standard Python asserts if you want, 
but it is recommended to use simple and readable asserts this library provides.

By default, even if you will use simple python assert like 

`assert 1==2` 

**checking** will give you a readable message, for example 

`Objects are not equals (1 != 2)`


###### Standard checks

```
#!python
@test
def checks_basic_asserts():
    is_true('1', 'Error message')   # checks, if the first arg equals to True
    is_false([], 'Error message')   # checks, if the first arg equals to False
    equals(1, 1, 'Error message')   # checks, if two args are equal (==)
    not_equals(1, 2, 'Error message')   # checks, if two args are NOT equal (!=)
    is_none(None, 'Error message')   # checks, if the first arg is None
    is_not_none('1', 'Error message')   # checks, if the first arg is not None
    contains(1, [1, 2, 3], 'Error message')   # checks, if the second arg contains the first arg
    not_contains(4, [1, 2, 3], 'Error message')   # checks, if the second arg does not contain the first arg
    is_zero(0, 'Error message')   # checks, if the first arg is equal to 0 (assumed to be int or float)
    is_positive(1, 'Error message')   # checks, if the first arg is greater than 0 (for int or float), or len of the arg is non-zero (for Sequence)
    is_negative(-1, 'Error message')   # checks, if the first arg is less than 0 (assumed to be int or float)
    is_empty([], 'Error message')   # checks, if the length of the first arg (Sized type) equals 0, e.g. a collection is empty
    is_not_empty([1,2], 'Error message')   # checks, if the length of first arg (Sized type) is greater than 0, e.g. a collection is NOT empty
```

Messages in all asserts are optional, but it is strongly recommended to use them.

###### Working with exceptions

If you need to check if the exception is raised or the message it contains, 
you can use the provided context manager:

```
#!python
@test
def check_with_exception():
    with waiting_exception(ZeroDivisionError) as e:
        x = 1 / 0 # Here exception will be raised!
    assert e.message == 'division by zero' # Check message (using python assert)

```

The test will fail if no exception is raised or the exception is of another type. 
Note that you have to check the exception message _after_ exiting the context manager, not within it's scope.

The library forbids the usage of the BaseException type here and it is strongly recommended not to use the Exception type as well. 
Use concrete exception types. 

In some cases you only need to run the code and make sure no exception is raised. 
There is a special way to do that:

```
#!python
@test
def no_exceptions_bad():
    do_something()   # Wrong: no asserts here, this is not a proper test.

@test
def check_no_exception_raises():
    with no_exception_expected():   # Correct: explicitly state that we do not expect any exceptions
        do_something()


```

The test fails if any exception is raised.

###### Managing test execution

Sometimes, you need to fail, skip or break a test during runtime due to some reason (wrong OS, wrong parameters, etc.)

```
#!python
@test
def must_fail_on_condition():
    if some_condition():
        test_fail('Expected to fail.')


@test
def must_be_broken():
    if some_condition():
        test_break('Expected to break.')

@test
def must_be_ignored():
    if some_condition():
        test_skip('Expected to be ignored.')
```

### Soft and Fluent Asserts ###

###### Soft Assert

Standard testing procedure implies the "fail fast" workflow: the whole test should halt if a single check fails. 
But sometimes you need to check a bunch of conditions and only fail if needed at the end of the test, 
collecting all of the information on the executed checks. 
Soft Assert is a simple and convenient tool to do that.

For example, you need to check all of the fields in a JSON object, 
collecting the info on which fields were correct and which were not: 

```
#!python

@test
def check_all_json_fields():
    my_json = fetch_json()

    soft_assert = SoftAssert()
    soft_assert.check(lambda : equals(1, my_json['field1'], 'message'))   # Check a field, the test will not stop executing on failure
    soft_assert.check(lambda : equals('text', my_json['field2'], 'message'))
    soft_assert.contains(1, my_json['list'])
    soft_assert.assert_all()   # The test will fail here if some of the checks failed earlier
```

**Attention!** 
You must use assert_all() at the end of the test to actually raise an assertion exception if something went wrong. 

###### Fluent Assert

Fluent assert is just syntactic sugar to make a series of checks for an object more simple and readable.
Fluent assert is **not** a soft assert, if one of the checks fails -- the whole chain halts.
Fluent assert interface has methods analogous to the basic asserts as well as exclusive ones:

```
#!python

@test
def check_fluents():
    my_list = get_my_list_somethere()

    # check if our object is not None, is instance of list, contains 2 and is sorted
    verify(my_list).is_not_none().AND.type_is(list).AND.contains(2).AND.is_sorted()

    some_object = SomeClass()
    same_object = some_object
    other_object = SomeClass()    
    # check if objects are the same, and are not same with another object
    verify(some_object).same_as(same_object).not_same_as(other_object)

    # check if 1 is in list [1, 2], not is in set{3, 4, 5} and is greater than 0
    verify(1).is_in([1, 2]).is_not_in({3, 4, 5}).greater_than(0)
```

There are special "switches" to check the size (length) of an object, or one of its attribute. 
Please note, that after after using a switch, you cannot return to the original object you started with.

```
#!python
@test
def switch_to_length():
    # check if the length of a list is positive and equals to 2 and is greater than length of [1]
    # the "size" is a switch -- all of the following checks will be executed against 
    # the int object (length of the starting object), NOT against the [1, 2] list
    verify([1,2]).size.is_positive().AND.equal(2).AND.greater_than_length_of([1]) 

@test
def switch_to_attribute():
    class Example:
        pass
    ex = Example()
    ex.x = 100

    # check if the object has attribute 'x' and whether it is equal to 100
    # the "attribute" method is a switch -- all of the following checks will be executed against 
    # the int object ('x' attribute of 'ex'), and NOT against 'ex' object itself
    verify(ex).has_attribute('x').AND.attribute('x').equal(100)
```

## Data Providers

Often you need to run the same test with different data, there is @provider annotation for that target. Mark function you want with @provider annotation and
you can use it in your tests. The function for data-provider should not have arguments and it has to return iterable, sequence or generator.

**Important!** Name of the provider has to be unique, you can specify it in parameter 

`@provider(name='provider')` 

or it takes the function name by default.
It it not necessary to have data-provider with the test (in the same module)

Data-provider takes values one by one and pushes it to your test.
```
#!python
# Create data-provider
@provider
def pairs():
    return [(1, 1, 2), (2, 2, 4)]  # Returns list of tuples


@test(data_provider='pairs')  # Specify what provider to use
def check_sum(it):  # Here we must have 1 argument for values of data-provider
    equals(it[0] + it[1], it[2])  # Checks sum of first and second elements of tuple equal to third element

```
You can specify mapping function to map values from the provider to some format, 
this string representation will be shown in test parameter, by default it use str(value) result.
Pay attention - mapping function just change parameter representation in logs, console or report, but not the values itself!


```
#!python
from checking import *


class Cat:
    def show(self):
        return f'Cat from {id(self)}'


@provider(map_to_str=Cat.show) # uses show() of Cat to show values
def cats():
    return (Cat(), Cat())


@test(data_provider='cats')
def check_cat(it):
    assert isinstance(it, Cat) # assert 'it' is a Cat object


if __name__ == '__main__':
    start(3)
```

In test logs you will see following information 

```text
Test "__main__.check_cat" [Cat from 140288585438160] SUCCESS!
----------
Test "__main__.check_cat" [Cat from 140288585437776] SUCCESS!
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
memory for your data and be smart when use it in parallel mode. DATA_FILE can use this parameter too.

```
#!python
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

@after_suite(always_run=True)
def another_func():
    print('will be printed, even if before_suite failed!')

```

## Mock, Double, Stub and Spy

For testing purposes you sometimes need to fake some behaviour or to isolate your application from any other classes/libraries etc.

If you need your test to use fake object, without doing any real calls, you can use mocks:


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
    with mock_builtins('input', lambda : 'test'): # Now input() just returns 'test', it does not wait for user input.
        result_text = our_weird_function_with_input_inside()
        equals('TEST', result_text)
```
More convenient way is to use mock_input or mock_print for simple and most common cases.
From code above we can test our_weird_function this way
```
#!python
@test
def check_input():
    with mock_input(['test']): # Now input() just returns 'test', it does not wait for user input.
        result_text = our_weird_function_with_input_inside()
        equals('TEST', result_text)

```

Now let's say we have simple function with print inside and need to test it:

```
#!python
def my_print(x):
    print(x)

@test
def check_print():
    with mock_print([]) as result: # now print just collects all to list result
        my_print(1)
        my_print('1')
    equals([1,'1'], result) # checks all args are in result list
```
and more complicated case, when our function works for ever, printing all inputs, until gets 'exit':

```
#!python
def use_both():
    while True:
        word = input('text>>>')
        if word == 'exit':
            break
        print(word)

@test
def check_print_and_input():
    # you can see inputs will get 'a','b' and 'exit' to break cycle, all args will
    # be collected to result list
    with mock_input(['a', 'b', 'exit']), mock_print([]) as result:
        use_both()
    equals(['a', 'b'], result)
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

**5. TestDouble object**

Test-Double object is like the Spy, but it saves original object behaviour, so its methods returns 
real object methods results if not specified otherwise.

```
#!python
@test
def check_double():
    spy = TestDouble("string")  # Create str double-object
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

### Function start() to runs test at module ###

You can execute all test at current module using function start(). For example:
```
#!python
from checking import *

@test
def some_check():
    equals(4, 2+2)


if __name__ == '__main__':
    start(3) # Here we run our test function some_check

```
There are parameters to run your tests in different ways:

**suite_name**  - name of the test-suite, to use in reports or in logs

**listener** - object of Listener class, test listener, is the way to work with test results and execution
DefaultListener is used by default. If set, then the verbose parameter is ignored (the one in the listener is used).

**verbose** is the report detail, 0 - briefly (only dots and 1 letter), 1 - detail, indicating only failed
tests, 2 - detail, indicating successful and fallen tests, 3 - detail and at the end, a list of fallen and broken ones
If verbose is not between 0 and 3, then 0 is accepted

Example (name and verbose)
```#!python
from checking import *


@test
def some_check():
    equals(4, 2 + 2)


@test
def some_check_two():
    equals(2, 1 + 1)


@test
def failed():
    equals(5, 2 + 2)  # Will fail


@test
def broken():
    int('a')  # Will be broken


if __name__ == '__main__':
    start(suite_name='My Suite', verbose=0)

```
This code will gave output (mention dots and chars!):
```text
Starting suite "My Suite"
..FB

==============================
Total tests: 4, success tests: 2, failed tests: 1, broken tests: 1, ignored tests: 0
Time elapsed: 0.00 seconds.
==============================
```
If you will use parameter verbose=3 in example above, result will be:

```text
Starting suite "My Suite"
----------
Test "__main__.some_check"  SUCCESS!
----------
Test "__main__.some_check_two"  SUCCESS!
----------
Test "__main__.failed"  FAILED!
File "\checking\runner.py", line 265, in _run_test
-->    test.run()
File "your_module_with_test_path", line 16, in failed
-->    equals(5, 2 + 2)  # Will fail
Objects are not equal!
Expected:"5" <int>
Actual  :"4" <int>!
----------
Test "__main__.broken"  BROKEN!
File "\checking\runner.py", line 265, in _run_test
-->    test.run()
File "your_module_with_test_path", line 21, in broken
-->    int('a')  # Will be broken
invalid literal for int() with base 10: 'a'

==============================
Total tests: 4, success tests: 2, failed tests: 1, broken tests: 1, ignored tests: 0
Time elapsed: 0.00 seconds.

Failed tests are:
     __main__.failed 

Broken tests are:
     __main__.broken 
==============================
```
**groups** is the list of test-group names to run. Only tests with that group will be run.

```
#!python
from checking import *


@test(groups=('api',))
def api_check():
    equals(4, 2 + 2)


@test(groups=('ui',))
def ui_check():
    equals(2, 1 + 1)


if __name__ == '__main__':
    start(verbose=3, groups=['api'])
```

When you runs this example, only function api_check will be executed, because we specify groups to run.


**params**  is the dictionary of parameters available in all tests (general run parameters)

```
#!python
from checking import *


@test
def api_check():
    equals(4, 2 + common_parameters['value']) # Here we use common_parameters - dictionary available from all tests


if __name__ == '__main__':
    start(verbose=3, params={'value': 2}) # Here we adds a parameter to common_parameters
```

**threads** is the number of threads to run tests, by default is 1. Each group can run in a separate thread if 
necessary. This is an experimental feature and it can be useful only for tests NOT performing any complex calculations (CPU bound).
It is best to use this parameter (more than 1) for tests related to the use of I / O  operations - disk work, network requests. Obey the GIL!

**dry_run** if True runs test-suite with fake function except of real tests and fixtures, can be useful to find out order, 
number of tests, params of provider etc. No real tests or fixtures will be executed!

**filter_by_name** if specified - runs only tests with name **containing** this parameter

```
#!python
from checking import *


@test
def api_check():
    equals(4, 2 + 2)


@test
def ui_check():
    equals(2, 1 + 1)


if __name__ == '__main__':
    start(verbose=3, filter_by_name='ui')

```
In example above only function ui_name will be runs, because name of the function (ui_check) contains 'ui'.

**random_order** if True - runs tests inside each group in random order. Can be useful to make sure your tests really independent as they should be.

**max_fail** if greater than 0, then suite will stops, when failed tests count reach that number. For example, if you specify max_fail=1,
then suite will stop after first failure. Pay attention that real failed test count can be bigger than max_fail if you use parallel execution, 
so parallel test will not interrupted until ends, even if count is reached.

**generate_report** if True - creates html report with the results in test folder. Experimental!

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

**-m int_argument**    runs all tests till not reach specified number of failed tests

**-R**    generate html-report with results of the tests


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
{
  "suite_name": "Default Test Suite",
  "verbose": 0,
  "groups": [],
  "params": {},
  "listener": "",
  "modules": [],
  "threads": 1,
  "dry_run": false,
  "filter_by_name": "",
  "random_order": false,
  "max_fail": 0,
  "generate_report": false
}
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
