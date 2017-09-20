import abc as _abc
import functools as _functools

from si.utils import singleton as _s


class ConstructBase(metaclass=_abc.ABCMeta):

  def __init__(self):
    self.reset()

  @property
  def obj(self):
    if self._obj is not _s.NotSet:
      return self._obj
    elif self._bytes is not _s.NotSet:
      self._obj = self.decode()
    return self._obj
  @obj.setter
  def obj(self, new_obj):
    del self.bytes
    self._obj = new_obj
  @obj.deleter
  def obj(self):
    self._obj = _s.NotSet

  @property
  def bytes(self):
    if self._bytes is not _s.NotSet:
      return self._bytes
    elif self._obj is not _s.NotSet:
      self._bytes = self.encode()
    return self._bytes
  @bytes.setter
  def bytes(self, new_bytes):
    del self.obj
    self._bytes = new_bytes
  @bytes.deleter
  def bytes(self):
    self._bytes = _s.NotSet

  def reset(self):
    if hasattr(self, 'default'):
      self.obj = self.default()
    else:
      self.obj = _s.NotSet

  @_abc.abstractmethod
  def encode(self):
    ...

  @_abc.abstractmethod
  def decode(self):
    ...

  @property
  def bitsize(self):
    return self._bitsize

  @classmethod
  def factory(cls, *args, **kwgs):
    return _functools.partial(cls, *args, **kwgs)

del _abc
