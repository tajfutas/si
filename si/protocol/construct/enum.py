import enum as _enum

from . import base as _base

from si.utils import singleton as _s


class Enum(_base.ConstructBase):

  def __init__(self, enum, bitsize):
    self._enum = enum
    self._bitsize = int(bitsize)
    super().__init__()

  # Below part allows to set obj as a string
  @property
  def obj(self):
    return _base.ConstructBase.obj.fget(self)
  @obj.setter
  def obj(self, new_obj):
    if (new_obj is not _s.NotSet
        and not isinstance(new_obj, _enum.Enum)):
      new_obj = self._enum.__getitem__(new_obj)
    return _base.ConstructBase.obj.fset(self, new_obj)
  @obj.deleter
  def obj(self):
    return _base.ConstructBase.obj.fdel(self)

  def decode(self):
    return self._enum(self.bytes)

  def encode(self):
    return self.obj.value

