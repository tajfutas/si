from si.protocol.codec import base as _codec
from si.protocol.codec import integer as _integer


class Command(_codec.Codec):

  @classmethod
  @_codec.decodemethod
  def decode(cls, data):
    assert len(data) == 2
    adr = _integer.Int8u.decode(data[0:1])
    anz = _integer.Int8u.decode(data[1:2])
    assert adr + anz <= 128
    return {'adr': adr, 'anz': anz}

  @classmethod
  @_codec.encodemethod
  def encode(cls, adr=0, anz=128):
    assert adr + anz <= 128
    b_adr = _integer.Int8u.encode(adr)
    b_anz = _integer.Int8u.encode(anz)
    return b_adr + b_anz


del _codec
