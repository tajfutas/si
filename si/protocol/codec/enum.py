import enum as _enum

from . import base as _base


class EnumCodec(_base.BaseCodec):

  enum = NotImplemented

  @classmethod
  def decode(cls, data):
    return cls.enum(data)

  @classmethod
  def encode(cls, obj):
    if not isinstance(obj, _enum.Enum):
      obj = cls.enum.__getitem__(obj)
    return obj.value


del _base
