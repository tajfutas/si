from si.codec import Codec as _Codec_


class ConstantCodec(_Codec_):

  data = NotImplemented

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    if data != cls.data:
      raise ValueError('invalid constant: '
          f'got {data!r}, expected {cls.data!r}')

  @classmethod
  @_Codec_.encodemethod
  def encode(cls):
    return cls.data


del _Codec_
