from . import base as _base


class ConstantCodec(_base.BaseCodec):

  data = NotImplemented

  @classmethod
  def decode(cls, data):
    if data != cls.data:
      raise ValueError('invalid constant: '
          f'got {data!r}, expected {cls.data!r}')

  @classmethod
  @_base.encodemethod
  def encode(cls):
    return cls.data


del _base
