from si.codec import Codec as _Codec_
from si.codec import IndexedData as _IndexedData_
from si.codec import integer as _integer_

# References:
# Communication.cs* 0917311 (#L3045-3073; #L3653-3883)
#     * named as cfg2
class BusTypeCodec(_Codec_):

  bitsize = 8
  subcodec = _integer_.Int8u

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data, data_idxs):
    i = data_idxs['CFG2']
    return cls.subcodec.decode(data[i:i+1])

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, value, data, data_idxs):
    data_idxs_ = data_idxs['CFG2'],
    enc_data = cls.subcodec.encode(value)
    return _IndexedData_(enc_data, data_idxs_)
  #keep _IndexedData_


codec = BusTypeCodec


del _Codec_
del _integer_
