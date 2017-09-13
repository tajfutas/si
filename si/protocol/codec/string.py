from . import base as _base


class FixedSizeStringCodec(_base.BaseCodec):

  bitsize = NotImplemented
  encoding = 'ascii'
  filler = ' '
  chars = NotImplemented

  @classmethod
  def decode(cls, data):
    return data.decode(cls.encoding)

  @classmethod
  def encode(cls, obj):
    fs = f'{{:{cls.filler}>{cls.chars}}}'
    objstr = str(obj)[:cls.chars]
    return fs.format(objstr).encode(cls.encoding)


del _base
