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

"""
This module provides base and utility classes which are all
subclasses of builtin bytes and which are do an automatic
serialization and deserialization of the object they represent.

The module provides base classes which should be subclassed and
customized for each object. See docstring of BaseBytes and the
particular base class for more information.

Base classes:
  * Bytes
  * Bits
  * DictBytes

The module provides some utility classes for the most common
cases. These classes does not have to get subclassed, but a
simple sublass with a pass could be reasonable to assigning a
name to the underlying object.

Utility classes:
  * PadBit
  * PadBits

For more information about instantiation, see help page of
BaseBytes class.
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
