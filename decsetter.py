import inspect

# https://docs.python.org/3/howto/descriptor.html#properties
# Emulate PyProperty_Type() in Objects/descrobject.c
class decorator_property(property):
    """Works just like @property but implements one more interface for setting the decorator callback. The property can then be used as a decorator."""

    def __init__(self, fget=None, fset=None, fdel=None, fdec=None, doc=None):
        super().__init__(fget, fset, fdel, doc)
        self.fdec = fdec

    def _init_inherit(self, fget=None, fset=None, fdel=None, fdec=None, doc=None):
        """Helper to initialise self from another instance of self"""
        return type(self)(
            self.fget if not fget else fget,
            self.fset if not fset else fset,
            self.fdel if not fdel else fdel,
            self.fdec if not fdec else fdec,
            self.__doc__ if not doc else doc,
        )

    @staticmethod
    def _isdecorator():
        """Hacky way of checking whether the caller (in this case __get__) is
        being called as a decorator"""
        stack = inspect.stack()
        if len(stack) > 1:
            # Code context of the parent frame of the caller
            context = stack[2].code_context
            if context:  # Context can be None
                context = context[0].strip()
                return context.startswith("@")  # and ...
        else:
            return False

    def __get__(self, obj, objtype=None):
        """Getter gets called when getting the property or when deforating the
        function. Return the appropriate function depending on the inferred
        context."""
        if obj is None:
            return self
        if self._isdecorator():
            if self.fdec is None:
                raise AttributeError("can't decorate with attribute")
            return self.fdec(obj)
        else:
            return super().__get__(obj, objtype)
            # if self.fget is None:
            #     raise AttributeError("unreadable attribute")
            # return self.fget(obj)

    def _setter_decor(self, fset):
        """Return an instance of decorator_property with fset and fdec set such
        that the fdec behaves as fset called with the decorated function as the
        argument"""

        def fdec(obj):
            def _decor(fun):
                fset(obj, fun)
                return fun

            return _decor

        return self._init_inherit(fset=fset, fdec=fdec)

    def setter(self, *fset, decorator=False):

        if len(fset) == 1 and callable(fset[0]):
            fset = fset[0]
            if decorator:
                return self._setter_decor(fset)
            else:
                return self._init_inherit(fset=fset)
        else:
            if decorator:
                return self._setter_decor
            else:

                def _setter(fset):
                    return self._init_inherit(fset=fset)

                return _setter

    def decor(self, fdec):
        return self._init_inherit(fdec=fdec)


# decorator_property has to be dropped into the namespace dict as opposed to
# imported since it has to be available at the class creation time -- that's
# when the property decorators are being called.
class DecoratorProperty(type):
    @classmethod
    def __prepare__(meta, *args, **kwargs):
        d = dict()
        d["decorator_property"] = decorator_property
        return d
