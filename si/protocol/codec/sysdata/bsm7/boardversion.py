from si.protocol.codec import base as _codec
from si.protocol.codec import integer as _integer

codec = _integer.Int8u.classfactory('BoardVersionCodec',
    mask=0b00001111)

del _integer
