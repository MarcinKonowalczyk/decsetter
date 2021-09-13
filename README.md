# decsetter

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
class ClassWithFunctions(metaclass=DecoratorProperty):
    def __init__(self):
        self._function_foo = None

    @decorator_property
    def function_foo(self):
        return self._function_foo

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

## Sharp corners

This of course doesn't work since `cwf` is not initialised at the time of decoration.

```python
...
@cwf.function_foo
def my_function(x):
    print("hello from my_function")
    return x ** 2

cwf = ClassWithFunctions()
cwf.function_foo(1)
# NameError: name 'cwf' is not defined
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
