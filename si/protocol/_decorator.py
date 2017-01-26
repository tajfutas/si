"""
Dataparts are always subclassed from the builtin bytes object
thus are immutable.

Each datapart represents a specific SI data and may be specific
by its way of construction and/or the extra methods which
convert the data into human readable forms.

The class decorators in this module are used to avoid deep
inheritance and code repetition.
"""

import enum
import functools
import math
import typing

from si.helper import classproperty


def default_if_none(from_val) -> 'decorator':
  # TODO: docstring
  @functools.wraps(from_val)
  def wrapped_from_val(cls, val):
    if val is None:
      return cls.default()
    else:
      return from_val(cls, val)
  return wrapped_from_val


def enum_defined(
    enumeration: enum.Enum,
  ) -> 'decorator':
  """
  Check value for enumeration membership

  Adds the matching enumeration as .enum property
  """

  def wrapped_decorator(cls):
    original_init = cls.__init__
    @functools.wraps(cls.__init__)
    def new_init(self, *args, **kwgs):
      original_init(self, *args[1:], **kwgs)
      self._enum = enumeration(self)
    cls.__init__ = new_init
    cls.enum = property(lambda self: self._enum,
        doc = "Corresponding {} enumeration".format(
            enumeration.__name__))
    return cls
  return wrapped_decorator




