from si.utils import enumhelper as _enumhelper

from si.protocol.codec import base as _codec


class EnumCodec(_codec.Codec):

  enum = NotImplemented
  subcodec = None

  @classmethod
  @_codec.decodemethod
  def decode(cls, data):
    if cls.subcodec is None:
      return cls.enum(data)
    else:
      return cls.enum(cls.subcodec.decode(data))

  @classmethod
  @_codec.encodemethod
  def encode(cls, obj):
    obj = _enumhelper.get(cls.enum, obj)
    if cls.subcodec is None:
      return obj.value
    else:
      return cls.subcodec.encode(obj.value)


del _codec
