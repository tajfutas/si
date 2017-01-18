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

def fixed_size(
    num_bytes: int = 0,
    num_bits: int = 0,
    endian: typing.Union['big', 'little'] = 'big'
  ) -> 'decorator':
  """
  Check size for match with the given parameters

  Raises ValueError if size does not match.

  If [0 < num_bits mod 8] then the rest of the bits are checked
  to be cleared.

  Raises OverflowError if those bits are not cleared.
  """
  assert num_bytes > 0 or num_bits > 0
  total_bits = 8 * num_bytes + num_bits
  total_bytes = math.ceil(total_bits / 8)
  set_mask = 2**total_bits - 1
  clear_mask = 2**(8*total_bytes) - 1 - set_mask

  def wrapped_decorator(cls):
    original_init = cls.__init__
    @functools.wraps(cls.__init__)
    def new_init(self, *args, **kwgs):
      original_init(self, *args[1:], **kwgs)
      if len(self) != total_bytes:
        efs = '{}: invalid length (expected {}): {}'
        raise ValueError(efs.format(cls.__name__,
            total_bytes, len(self)))
      intval = int.from_bytes(self, endian)
      if intval & clear_mask:
        efs = '{}: out of range (expected <= {}): {}'
        raise OverflowError(efs.format(cls.__name__,
            set_mask, intval))
    cls.__init__ = new_init
    if num_bits > 0:
      cls._bits = classproperty(
          lambda cls, total_bits=total_bits: total_bits,
          doc = 'Number of bits')
    return cls
  return wrapped_decorator


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
