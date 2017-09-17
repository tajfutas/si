from si.protocol.codec import base as _codec



class FixedSizeStringCodec(_codec.Codec):

  bitsize = NotImplemented
  encoding = 'ascii'
  filler = ' '
  chars = NotImplemented

  @classmethod
  @_codec.decodemethod
  def decode(cls, data):
    return data.decode(cls.encoding)

  @classmethod
  @_codec.encodemethod
  def encode(cls, obj):
    fs = f'{{:{cls.filler}>{cls.chars}}}'
    objstr = str(obj)[:cls.chars]
    return fs.format(objstr).encode(cls.encoding)


del _codec
