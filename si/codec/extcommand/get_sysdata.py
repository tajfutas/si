from si.codec import Codec as _Codec_
from si.codec import integer as _integer_


class GetSysDataCommandCodec(_Codec_):

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    assert len(data) == 2
    adr = _integer_.Int8u.decode(data[0:1])
    anz = _integer_.Int8u.decode(data[1:2])
    assert adr + anz <= 128
    return {'adr': adr, 'anz': anz}
  #keep _integer_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, adr=0, anz=128):
    assert adr + anz <= 128
    b_adr = _integer_.Int8u.encode(adr)
    b_anz = _integer_.Int8u.encode(anz)
    return b_adr + b_anz
  #keep _integer_


codec = GetSysDataCommandCodec


del _Codec_
