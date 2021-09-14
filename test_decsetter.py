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


##################################################


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


def test_setter_kwarg_true():
    """With decorator=true the parameter should be setable with a decorator"""
    o = SetterKwargTrue()

    o.fun = lambda x: x ** 2
    assert o.fun(4) == 16

    @o.fun
    def my_function(x):
        return x ** 3

    assert o.fun(4) == 64


@pytest.mark.parametrize(
    "cls",
    (Setter, SetterKwargFalse, SetterKwargTrue),
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
