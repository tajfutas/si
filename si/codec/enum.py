from si.utils import enumhelper as _enumhelper_

from si.codec import Codec as _Codec_


class EnumCodec(_Codec_):

  enum = NotImplemented
  subcodec = None

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    if cls.subcodec is None:
      return cls.enum(data)
    else:
      return cls.enum(cls.subcodec.decode(data))

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, obj):
    obj = _enumhelper_.get(cls.enum, obj)
    if cls.subcodec is None:
      return obj.value
    else:
      return cls.subcodec.encode(obj.value)
  #keep _enumhelper_


del _Codec_
