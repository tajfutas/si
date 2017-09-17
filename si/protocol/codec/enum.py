from si.protocol.codec import base as _codec


class EnumCodec(_codec.Codec):

  enum = NotImplemented

  @classmethod
  @_codec.decodemethod
  def decode(cls, data):
    return cls.enum(data)

  @classmethod
  @_codec.encodemethod
  def encode(cls, obj):
    if not isinstance(obj, cls.enum):
      obj = cls.enum.__getitem__(obj)
    return obj.value


del _codec
