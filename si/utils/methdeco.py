from functools import wraps


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


def default_if_none(m):
  # TODO: improve, docstring
  @wraps(m)
  def wrapped(cls, val):
    if val is None:
      return cls.default()
    else:
      return m(cls, val)
  return wrapped
