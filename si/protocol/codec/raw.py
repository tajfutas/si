from si.protocol.codec import base as _codec



class RawCodec(_codec.Codec):

  bitsize = ...

  @classmethod
  @_codec.decodemethod
  def decode(cls, data):
    if cls.bitsize != ...:
      assert len(data) == cls.bitsize
    return data

  @classmethod
  @_codec.encodemethod
  def encode(cls, data):
    if cls.bitsize != ...:
      assert len(data) == cls.bitsize
    return data


del _codec
