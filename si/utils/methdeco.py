import functools as _functools_


# http://stackoverflow.com/a/5192374/2334951
# http://stackoverflow.com/a/17330273/2334951
# http://stackoverflow.com/a/11768768/2334951
class classproperty:

  def __init__(self, fget, doc=None):
    self.fget = fget
    if doc is None and fget is not None:
      doc = fget.__doc__
    # docstring got lost
    self.__doc__ = doc

  def __get__(self, obj, objtype=None):
    if objtype is None:
      objtype = type(obj)
    return self.fget(objtype)

  def __set__(self, obj, value):
    if self.fset is None:
      raise AttributeError("can't set class attribute")

  def __delete__(self, obj):
    if self.fdel is None:
      raise AttributeError("can't delete class attribute")


def eliminate_first_arg_if_none(m):
  # TODO: improve, docstring
  @_functools_.wraps(m)
  def wrapped(cls, *args, **kwgs):
    if args and args[0] is None:
      return m(cls, *args[1:], **kwgs)
    else:
      return m(cls, *args, **kwgs)
  return wrapped


def none_if_first_arg_is_none(m):
  # TODO: improve, docstring
  @_functools_.wraps(m)
  def wrapped(cls, *args, **kwgs):
    if args and args[0] is None:
      return None
    else:
      return m(cls, *args, **kwgs)
  return wrapped
