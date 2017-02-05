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
