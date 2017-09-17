from si.protocol.codec import base as _codec


class ConstantCodec(_codec.Codec):

  data = NotImplemented

  @classmethod
  @_codec.decodemethod
  def decode(cls, data):
    if data != cls.data:
      raise ValueError('invalid constant: '
          f'got {data!r}, expected {cls.data!r}')

  @classmethod
  @_codec.encodemethod
  def encode(cls):
    return cls.data


del _codec
