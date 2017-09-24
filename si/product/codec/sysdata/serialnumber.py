from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.codec import integer as _integer_
from si.product import \
  ProductFamily as _ProductFamily_
from . import productfamily as _productfamily_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3073; #L3653-3855)
class SerialNumberCodec(_Codec_):

  bitsize = 40

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    bn3, bn2, bn1, bn0, cfg0 = data
    pfam = _productfamily_.codec.decode([cfg0])
    bn3 = (0 if pfam is _ProductFamily_.SimSrr else bn3)
    return _integer_.Int32ub.decode(bytes([bn3]) + data[1:4])
  #keep _integer_
  #keep _productfamily_
  #keep _ProductFamily_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, value, *,
      data=None, data_idxs=None):
    pfam = _ProductFamily_.NotSet
    data_ = None
    mask = [255, 255, 255, 255, 0]
    if data_idxs:
      data_ = bytes(data[i] for i in data_idxs)
    elif data is not None:
      data_ = data
    if data_:
      pfam = _productfamily_.codec.decode(data_[4:5])
    if pfam is _ProductFamily_.SimSrr:
      assert value < 256**3
      mask[0] = 0
    enc_data = (
      _integer_.Int32ub.encode(value)
      + _productfamily_.codec.encode(pfam)
    )
    return _MaskedData_(enc_data, mask)
  #keep _integer_
  #keep _MaskedData_
  #keep _productfamily_
  #keep _ProductFamily_


codec = SerialNumberCodec


del _Codec_
