import enum
import functools
import typing

from si.helper import classproperty


def default_if_none(from_val) -> typing.Callable:
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
  ) -> typing.Type['_base.BaseBytes']:
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
