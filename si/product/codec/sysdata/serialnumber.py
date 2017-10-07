from si.codec import Codec as _Codec_
from si.codec import MaskedIndexedData as _MaskedIndexedData_
from si.codec import integer as _integer_
from si.product import \
  ProductFamily as _ProductFamily_
from . import productfamily as _productfamily_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3073; #L3653-3855)
class SerialNumberCodec(_Codec_):

  bitsize = 32
  subcodec = _integer_.Int32ub

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data, idxmap):
    data_keys = ('BN3', 'BN2', 'BN1', 'BN0')
    idxs = tuple(idxmap[key] for key in data_keys)
    data_ = [data[i] for i in idxs]
    pfam = _productfamily_.codec.decode(data, idxmap)
    if pfam is _ProductFamily_.SimSrr:
      data_[0] = 0
    return cls.subcodec.decode(data_)
  #keep _productfamily_
  #keep _ProductFamily_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, value, data, idxmap):
    data_keys = ('BN3', 'BN2', 'BN1', 'BN0')
    idxs = tuple(idxmap[key] for key in data_keys)
    mask = bytearray((255 for _ in data_keys))
    pfam = _productfamily_.codec.decode(data, idxmap)
    if pfam is _ProductFamily_.SimSrr:
      assert value < 256**3
      mask[0] = 0
    enc_data = bytearray(cls.subcodec.encode(value))
    return _MaskedIndexedData_(enc_data, idxs, mask)
  #keep _MaskedIndexedData_
  #keep _productfamily_
  #keep _ProductFamily_


codec = SerialNumberCodec


del _Codec_
del _integer_
