# README #

A simple library to test your python code.

Key Features:



 * no third-party dependencies, only the standard library is used
 * no need to inherit from any classes
 * no need to name your files and/or tests with the prefix 'test' added
 * it is possible to use native python assert python as well as library asserts
 * simple and understandable work with tests, data providers, checks
 * the ability to run based on a file with settings or passing arguments on the command line
 * automatic search for all tests in the current folder and subfolders
 * flexible configuration of both tests and their groups, the ability to group tests and run only selected groups
 * the ability to use both the built-in results processing tool and write your own
 * the ability to group, stop the test by timeout, parallel launch without installing additional plugins


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




### Contact me ###
Lexman2@yandex.ru