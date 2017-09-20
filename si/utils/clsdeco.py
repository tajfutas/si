import enum as _enum_
import functools as _functools_


def enum_defined(enum: _enum_.Enum):
  """
  Atomatically check for enum membership at the end of
  initialization.

  Adds the matching enum as .enum property.
  """
  def wrapped_decorator(cls):
    original_init = cls.__init__
    @_functools_.wraps(cls.__init__)
    def new_init(self, *args, **kwgs):
      original_init(self, *args[1:], **kwgs)
      self._enum = enum(self)
    cls.__init__ = new_init
    cls.enum = property(
      lambda self: self._enum,
      doc = f'Corresponding {enum.__name__} enumeration',
    )
    return cls
  return wrapped_decorator
#keep _functools_


del _enum_
