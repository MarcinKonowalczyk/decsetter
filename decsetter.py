import inspect

# https://docs.python.org/3/howto/descriptor.html#properties
class Property:
    "Emulate PyProperty_Type() in Objects/descrobject.c"

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)


class decorator_property(Property):
    """Emulate PyProperty_Type() in Objects/descrobject.c"""

    def __init__(self, fget=None, fset=None, fdel=None, fdec=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self.fdec = fdec

    @staticmethod
    def _isdecorator():
        isdecorator = False
        stack = inspect.stack()
        if len(stack) > 1:
            # Code context of the parent frame of the caller
            context = stack[2].code_context
            if context:  # Context can be None
                context = context[0].strip()
                isdecorator = context.startswith("@")  # and ...
        return isdecorator

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self._isdecorator():
            if self.fdec is None:
                raise AttributeError("can't decorate with attribute")
            return self.fdec(obj)
        else:
            if self.fget is None:
                raise AttributeError("unreadable attribute")
            return self.fget(obj)

    def setter(self, *fset, decorator=False):

        if len(fset) == 1 and callable(fset[0]):
            fset = fset[0]
            if decorator:

                def _fdec(obj):
                    def _decor(fun):
                        fset(obj, fun)
                        return fun

                    return _decor

                return type(self)(self.fget, fset, self.fdel, _fdec, self.__doc__)
            else:
                return type(self)(self.fget, fset, self.fdel, self.fdec, self.__doc__)
        else:
            if decorator:

                def _setter_decor(fset):
                    def _fdec(obj):
                        def _decor(fun):
                            fset(obj, fun)
                            return fun

                        return _decor

                    return type(self)(self.fget, fset, self.fdel, _fdec, self.__doc__)

                return _setter_decor
            else:

                def _setter(fset):
                    return type(self)(
                        self.fget, fset, self.fdel, self.fdec, self.__doc__
                    )

                return _setter

    def decor(self, fdec):
        return type(self)(self.fget, self.fset, self.fdel, fdec, self.__doc__)


class DecoratorProperty(type):
    @classmethod
    def __prepare__(meta, *args, **kwargs):
        d = dict()
        d["decorator_property"] = decorator_property
        return d
