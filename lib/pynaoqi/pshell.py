# -*- coding: utf-8 -*-
"""
    pshell
    ~~~~~~

    Helpers for dumping a shell into a file and load back from there.  Based
    on the python cookbook `recipe 572213`_ by Oren Tirosh.

    Dumping::

        >>> import pshell
        >>> def foo(a, b):
        ...     return a + b
        ...
        >>> pshell.dump('shell.dump')

    And loading::

        >>> import pshell
        >>> pshell.load()
        >>> foo(1, 2)
        3

    .. _recipe 572213: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/572213

    :copyright: Copyright 2008 by Armin Ronacher.
    :license: BSD.
"""
import __builtin__
import __main__ as _main_module
import sys
import marshal
import ctypes
from pickle import Pickler, Unpickler
from types import CodeType, FunctionType, ClassType, MethodType, \
     ModuleType, GetSetDescriptorType, BuiltinMethodType


CellType = type((lambda x: lambda y: x)(0).func_closure[0])
WrapperDescriptorType = type(type.__repr__)


def dump(filename='/tmp/console.sess', main_module=_main_module):
    """Dump the main module into a session file."""
    f = file(filename, 'wb')
    try:
        pickler = ShellPickler(f, 2)
        pickler._main_module = main_module
        pickler.dump(main_module)
    finally:
        f.close()


def load(filename='/tmp/console.sess', main_module=_main_module):
    """Update the main module with the state from the session file."""
    f = file(filename, 'rb')
    try:
        unpickler = ShellUnpickler(f)
        unpickler._main_module = main_module
        module = unpickler.load()
        main_module.__dict__.update(module.__dict__)
    finally:
        f.close()


class ShellPickler(Pickler):
    dispatch = Pickler.dispatch.copy()
    _main_module = None


class ShellUnpickler(Unpickler):
    _main_module = None

    def find_class(self, module, name):
        if (module, name) == ('__builtin__', '__main__'):
            return self._main_module.__dict__
        return Unpickler.find_class(self, module, name)


def register(t):
    def proxy(func):
        ShellPickler.dispatch[t] = func
        return func
    return proxy


def _create_typemap():
    import types
    for key, value in types.__dict__.iteritems():
        if getattr(value, '__module__', None) == '__builtin__' and \
           type(value) is type:
            yield value, key
_typemap = dict(_create_typemap(), **{
    CellType:                   'CellType',
    WrapperDescriptorType:      'WrapperDescriptorType'
})
_reverse_typemap = dict((v, k) for k, v in _typemap.iteritems())


def _unmarshal(string):
    return marshal.loads(string)


def _load_type(name):
    return _reverse_typemap[name]


def _create_type(type, *args):
    return type(*args)


def _create_cell(obj):
    d = {}
    p = ctypes.pythonapi.PyCell_New(ctypes.py_object(obj))
    ctypes.pythonapi.PyDict_SetItemString(ctypes.py_object(d), 'x', p)
    return d['x']


def _import_module(import_name):
    if '.' in import_name:
        items = import_name.split('.')
        module = '.'.join(items[:-1])
        obj = items[-1]
    else:
        return __import__(import_name)
    return getattr(__import__(module, None, None, [obj]), obj)


def _locate_function(obj):
    if obj.__module__ == '__main__':
        return False
    try:
        found = _import_module(obj.__module__ + '.' + obj.__name__)
    except:
        return False
    return found is obj


@register(CodeType)
def save_code(pickler, obj):
    pickler.save_reduce(_unmarshal, (marshal.dumps(obj),), obj=obj)


@register(FunctionType)
def save_function(pickler, obj):
    if not _locate_function(obj):
        pickler.save_reduce(FunctionType, (obj.func_code, obj.func_globals,
                                           obj.func_name, obj.func_defaults,
                                           obj.func_closure), obj=obj)
    else:
        Pickler.save_global(pickler, obj)


@register(dict)
def save_module_dict(pickler, obj):
    if obj is pickler._main_module.__dict__:
        pickler.write('c__builtin__\n__main__\n', obj=obj)
    else:
        Pickler.save_dict(pickler, obj)


@register(ClassType)
def save_classobj(pickler, obj):
    if obj.__module__ == '__main__':
        pickler.save_reduce(ClassType, (obj.__name__, obj.__bases__,
                                        obj.__dict__), obj=obj)
    else:
        Pickler.save_global(pickler, obj)


@register(MethodType)
def save_instancemethod(pickler, obj):
    pickler.save_reduce(MethodType, (obj.im_func, obj.im_self,
                                     obj.im_class), obj=obj)


@register(BuiltinMethodType)
def save_builtin_method(pickler, obj):
    if obj.__self__ is not None:
        pickler.save_reduce(getattr, (obj.__self__, obj.__name__), obj=obj)
    else:
        Pickler.save_global(pickler, obj)


@register(GetSetDescriptorType)
@register(WrapperDescriptorType)
def save_wrapper_descriptor(pickler, obj):
    pickler.save_reduce(getattr, (obj.__objclass__, obj.__name__), obj=obj)


@register(CellType)
def save_cell(pickler, obj):
    pickler.save_reduce(_create_cell, (obj.cell_contents,), obj=obj)


@register(ModuleType)
def save_module(pickler, obj):
    if obj is pickler._main_module:
        pickler.save_reduce(__import__, (obj.__name__,), obj=obj,
                            state=obj.__dict__.copy())
    else:
        pickler.save_reduce(_import_module, (obj.__name__,), obj=obj)


@register(type)
def save_type(pickler, obj):
    if obj in _typemap:
        pickler.save_reduce(_load_type, (_typemap[obj],), obj=obj)
    elif obj.__module__ == '__main__':
        pickler.save_reduce(_create_type, (type(obj), obj.__name__,
                                           obj.__bases__, obj.__dict__),
                                           obj=obj)
    else:
        Pickler.save_global(pickler, obj)
