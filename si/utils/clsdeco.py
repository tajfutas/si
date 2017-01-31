import enum
import functools


def enum_defined(enumeration: enum.Enum):
  """
  Atomatically check for enumeration membership at the end of
  initialization.

  Adds the matching enumeration as .enum property.
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
