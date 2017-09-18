from si.protocol import station as _station
from si.protocol.codec import enum as _enum
from si.protocol.codec import integer as _integer

# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3023-3029)
codec = _enum.EnumCodec.classfactory('ProductFamilyCodec',
    enum=_station.ProductFamily, subcodec=_integer.Int8u)


del _station
del _enum
del _integer
