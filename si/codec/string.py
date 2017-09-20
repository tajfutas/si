from si.codec import Codec as _Codec_


class FixedSizeStringCodec(_Codec_):

  encoding = 'ascii'
  filler = ' '
  chars = NotImplemented

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    return data.decode(cls.encoding)

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, obj):
    fs = f'{{:{cls.filler}>{cls.chars}}}'
    objstr = str(obj)[:cls.chars]
    return fs.format(objstr).encode(cls.encoding)


del _Codec_
