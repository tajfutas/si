"""
This library is a lightweight builder and parser of binary data.

All of the objbytes objects are subclassed from the builtin
bytes class, thus they contain the raw bytes of the underlying
data by definition.

All of the objbytes objects is usually done by either passing
the underlying object (serialization) or the raw data bytes.
Whether the argument should be parsed or not is detected
effciently (see help of the base module).

The library provides objects for varios common data structures
which may or may not need to get subclassed for the individual
needs. Nameing objects is also done by by subclassing. There are
class factory methods to do dynamical subclassing when required.

Customization is usually done by defining some methods of the
subclassed objbytes object. For more info see help page of
objbytes.base module.
"""


__all__ = [
    'base',
    'factorymethod',
    'collections',
    'pad',
    ]


from . import base
from . import factorymethod
from . import types_ as types
