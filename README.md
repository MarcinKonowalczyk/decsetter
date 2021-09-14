# Decorator @property setter

[![tests](https://github.com/MarcinKonowalczyk/decsetter/actions/workflows/main.yml/badge.svg)](https://github.com/MarcinKonowalczyk/decsetter/actions/workflows/main.yml) [![Coverage Status](https://coveralls.io/repos/github/MarcinKonowalczyk/decsetter/badge.svg?branch=master)](https://coveralls.io/github/MarcinKonowalczyk/decsetter?branch=master)


Setting `DecoratorProperty` as the metaclass adds a `@decorator_property` decorator to the body of the function. `decorator_property` behaves just like python's builtin [property](https://docs.python.org/3/library/functions.html#property), but it provides an additional interface for interacting with the property via a decorator.


## Usage

A typical usage is for setting properties of instances which are also functions. Here is a minimal working example:

```python
from decsetter import DecoratorProperty

class ClassWithFunctions(metaclass=DecoratorProperty):
    def __init__(self):
        self._function_foo = None

    @decorator_property
    def function_foo(self):
        return self._function_foo

    @function_foo.setter(decorator=True)
    def function_foo(self, value):
        self._function_foo = value

# Instantiate the class
cwf = ClassWithFunctions()

# Set cwf.function_foo to `my_function`
# with normal @property this would not work
@cwf.function_foo
def my_function(x):
    print("hello from my_function")
    return x ** 2

print(cwf.function_foo(4))
```

You can also use the `@<function_name>.decor` decorator to specify your own decorator callback. This way you can add side-effects to the decorator (you could even make it not set the value but do something completely different). In this case the decorator prints `"hello from decor"` at decoration time.

```python
...

@function_foo.setter
def function_foo(self, value):
    self._function_foo = value

@function_foo.decor
def function_foo(self):
    def decor(fun):
        print("hello from decor")
        self._function_foo = fun
        return fun
    return decor

...
```

Note that, similarly to decorators with arguments, the function decorated with `@function_foo.decor` has to return the decorator. The internal property `_function_foo` is set by reference to the instance of the class encapsulated in the closure of `decor`.


The decorator does not have to be a setter. In the following example the decorator of an integer property `incr` decorates the function to run `incr` number of times while incrementing its input.

```python
from decsetter import DecoratorProperty
from functools import wraps

class FunctionRepeater(metaclass=DecoratorProperty):
    """Decorator of property 'incr' runs the wrapped function n times"""

    def __init__(self, incr=1):
        self._incr = incr

    @decorator_property
    def incr(self):
        return self._incr

    @incr.setter
    def incr(self, value):
        self._incr = value

    @incr.decor
    def incr(self):
        def outer_wrapper(fun):
            @wraps(fun)
            def inner_wrapper(x, **kwargs):
                return tuple(fun(x + i, **kwargs) for i in range(self._incr))

            return inner_wrapper

        return outer_wrapper
```

It can be used as follows:

```python
repeat = FunctionRepeater(3)

@repeat.incr
def square(x):
    return x ** 2

square(1) # -> (1, 4, 9)
square(3) # -> (9, 16, 25)
```

The decorated `square` keeps a reference to instance of `FunctionRepeater` such that if the value of 

```python
repeat.incr = 5
square(3) # -> (9, 16, 25, 36, 49)
```

## Sharp corners

This of course doesn't work since `cwf` is not initialised at the time of decoration.

```python
...
@cwf.function_foo
def my_function(x):
    print("hello from my_function")
    return x ** 2

# ^ Throws NameError: name 'cwf' is not defined

cwf = ClassWithFunctions()
```

If you want to define your function before instantiating the class, just use normal way of setting properties:

```python
def my_function(x):
    print("hello from my_function")
    return x ** 2

cwf = ClassWithFunctions()
cwf.function_foo = my_function
cwf.function_foo(1)
```


## Dev

Run coverage locally:
```
coverage run --omit="test_*.py" -m pytest && coverage html && open htmlcov/index.html 
```
