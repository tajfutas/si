from si.protocol.codec import base as _codec
from si.protocol.codec import string as _string

# References:
# Communication.cs 0917311 (#L2995-3005)
class FirmwareVersion(_string.FixedSizeStringCodec):
  bitsize=24
  encoding='iso8859-1'
  filler='0'
  chars=3

  @classmethod
  @_codec.decodemethod
  def decode(cls, data):
    return int(_string.FixedSizeStringCodec.decode(data))

codec = FirmwareVersion

del _codec
