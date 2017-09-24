from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.codec import integer as _integer_
from si.product import \
  ProductFamily as _ProductFamily_
from . import productfamily as _productfamily_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3121-3131)
class BatteryCapacityCodec(_Codec_):

  bitsize = 32

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    pfam = _productfamily_.codec.decode(data[-1:])
    if (
        pfam is _ProductFamily_.Bs8SiMaster
        or pfam - _ProductFamily_.Bsx7 <= 4
        or pfam is _ProductFamily_.SiGsmDn
    ):
      bcap = _integer_.Int32ub.decode(data[0:4])
      bcap /= 3600.0
      bcap = (0.0 if bcap >= 100000.0 else bcap)
      return bcap
  #keep _integer_
  #keep _productfamily_
  #keep _ProductFamily_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, *value,
      data=None, data_idxs=None):
    assert (0<= len(value) < 2)
    value = (None if not value else value[0])
    pfam = _ProductFamily_.NotSet
    data_ = None
    if data_idxs:
      data_ = bytes(data[i] for i in data_idxs)
    elif data is not None:
      data_ = data
    if data_:
      pfam = _productfamily_.codec.decode(data_[-1:])
    if (
        pfam is _ProductFamily_.Bs8SiMaster
        or pfam - _ProductFamily_.Bsx7 <= 4
        or pfam is _ProductFamily_.SiGsmDn
    ):
      if value >= 100000.0:
        raise ValueError(
            'invalid value; '
            'expected value in range(0, 100000)'
        )
      enc_data = (
          _integer_.Int32ub.encode(int(value*3600))
          + _productfamily_.codec.encode(pfam)
      )
      mask = [255, 255, 255, 255, 0]
      return _MaskedData_(enc_data, mask)
    elif value is not None:
      raise TypeError(
          'invalid value; '
          'expected None value or different ProductFamily'
      )
  #keep _integer_
  #keep _MaskedData_
  #keep _productfamily_
  #keep _ProductFamily_


codec = BatteryCapacityCodec


del _Codec_
