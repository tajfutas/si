from si.protocol.codec import string as _string

# References:
# Communication.cs 0917311 (#L2995-3005)
codec = _string.FixedSizeStringCodec.classfactory(
    'FirmwareVersion',
    bitsize=24,
    encoding='iso8859-1',
    filler='0',
    chars=3,
  )


del _string
