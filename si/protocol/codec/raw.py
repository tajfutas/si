from . import base as _base


class RawCodec(_base.BaseCodec):

  bitsize = ...

  @classmethod
  def decode(cls, data):
    if cls.bitsize != ...:
      assert len(data) == cls.bitsize
    return data

  encode = decode
