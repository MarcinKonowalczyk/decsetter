from decsetter import DecoratorProperty
import pytest


class Common(metaclass=DecoratorProperty):
    """Common __init__ and decorated property for the test classes"""

    def __init__(self):
        self._fun = None
        self.sideeffect = False

    @decorator_property
    def fun(self):
        return self._fun

    @staticmethod
    def sideeffect_decorator(obj):
        """ """

        def decor(fun):
            obj._fun = fun
            obj.sideeffect = True
            return fun

        return decor


##### Class definitions for the tests ############


class Setter(Common):
    fun = Common.fun

    @fun.setter
    def fun(self, value):
        self._fun = value


class SetterKwargTrue(Common):
    fun = Common.fun

    @fun.setter(decorator=True)
    def fun(self, value):
        self._fun = value


class SetterKwargFalse(Common):
    fun = Common.fun

    @fun.setter(decorator=False)
    def fun(self, value):
        self._fun = value


class SetterKwargTrueNoDecor(Common):
    fun = Common.fun

    def fset(self, value):
        self._fun = value

    fun = fun.setter(fset, decorator=True)


class SetterAndDecor(Common):
    fun = Common.fun

    @fun.setter
    def fun(self, value):
        self._fun = value

    @fun.decor
    def fun(self):
        return Common.sideeffect_decorator(self)


class SetterAndDecorKwargTrue(Common):
    fun = Common.fun

    @fun.setter(decorator=True)
    def fun(self, value):
        self._fun = value

    @fun.decor
    def fun(self):
        return Common.sideeffect_decorator(self)


class SetterAndDecorKwargFalse(Common):
    fun = Common.fun

    @fun.setter(decorator=False)
    def fun(self, value):
        self._fun = value

    @fun.decor
    def fun(self):
        return Common.sideeffect_decorator(self)


class JustDecor(Common):
    fun = Common.fun

    @fun.decor
    def fun(self):
        return Common.sideeffect_decorator(self)


##### Basic tests ################################


@pytest.mark.parametrize("cls", (Setter, SetterKwargFalse))
def test_setter(cls):
    """With decorator=false the parameter should *not* be setable with a decorator"""
    o = cls()

    o.fun = lambda x: x ** 2
    assert o.fun(4) == 16

    with pytest.raises(AttributeError, match=r".+decorat.+"):

        @o.fun
        def my_function(x):
            return x ** 2


@pytest.mark.parametrize("cls", (SetterKwargTrue, SetterKwargTrueNoDecor))
def test_setter_kwarg_true(cls):
    """With decorator=true the parameter should be setable with a decorator"""
    o = cls()

    o.fun = lambda x: x ** 2
    assert o.fun(4) == 16

    @o.fun
    def my_function(x):
        return x ** 3

    assert o.fun(4) == 64


@pytest.mark.parametrize(
    "cls",
    (Setter, SetterKwargFalse, SetterKwargTrue, SetterKwargTrueNoDecor),
)
def test_setter_sideeffect(cls):
    """Setter should not have a sideeffect"""
    o = cls()
    o.fun = lambda x: x ** 2
    assert o.sideeffect == False


@pytest.mark.parametrize(
    "cls",
    (SetterAndDecor, SetterAndDecorKwargFalse, SetterAndDecorKwargTrue, JustDecor),
)
def test_setter_and_decor(cls):
    """Parameter should be settable with custom decortor"""
    o = cls()

    @o.fun
    def my_function(x):
        return x ** 3

    assert o.fun(4) == 64


@pytest.mark.parametrize(
    "cls",
    (SetterAndDecor, SetterAndDecorKwargFalse, SetterAndDecorKwargTrue, JustDecor),
)
def test_sideeffect(cls):
    """Custom decorator should have a sideeffect"""
    o = cls()

    @o.fun
    def my_function(x):
        ...

    assert o.sideeffect == True


##################################################


class NoGetter(metaclass=DecoratorProperty):
    def setx(self, value):
        self._x = value

    x = property(None, setx)

    def indirect_getx(self):
        return self._x


def test_no_getter():
    o = NoGetter()

    o.x = 1
    assert o.indirect_getx() == 1

    o.x = 2
    assert o.indirect_getx() == 2

    with pytest.raises(AttributeError):
        print(o.x)


##################################################

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


def test_different_decor():
    repeat = FunctionRepeater(3)

    @repeat.incr
    def square(x):
        return x ** 2

    assert square(1) == (1, 4, 9)
    assert square(3) == (9, 16, 25)

    repeat.incr = 5

    assert square(3) == (9, 16, 25, 36, 49)
