from si.codec import Codec as _Codec_


class RawCodec(_Codec_):

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    if cls.bitsize != ...:
      assert len(data) == cls.bitsize
    return data

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, data):
    if cls.bitsize != ...:
      assert len(data) == cls.bitsize
    return data


del _Codec_
