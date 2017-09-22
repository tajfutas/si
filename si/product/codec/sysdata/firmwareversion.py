from si.codec import Codec as _Codec_
from si.codec import string as _string_


# References:
# Communication.cs 0917311 (#L2995-3005)
class FirmwareVersionCodec(_string_.FixedSizeStringCodec):
  bitsize=24
  encoding='iso8859-1'
  filler='0'
  chars=3

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    return int(_string_.FixedSizeStringCodec.decode(data))
  #keep _string_


codec = FirmwareVersionCodec


del _Codec_
