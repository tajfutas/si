from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.codec import integer as _integer_
from si.product import \
  ProductFamily as _ProductFamily_
from . import _constant as _C_
from . import productfamily as _productfamily_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3073; #L3653-3855)
class BackupMemorySizeCodec(_Codec_):

  bitsize = 16

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    bms, cfg0 = data
    pfam = _productfamily_.codec.decode([cfg0])
    if (
        pfam is _ProductFamily_.Bs8SiMaster
        or pfam - _ProductFamily_.Bsx7 <= 4
        or pfam is _ProductFamily_.SiGsmDn
    ):
      return (0 if bms == _C_.BMS_ZEROVALUE else bms)
    else:
      return _C_.BMS_DEFAULT
  #keep _C_
  #keep _productfamily_
  #keep _ProductFamily_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, value, *,
      data=None, data_idxs=None):
    bms = _C_.BMS_DEFAULT
    pfam = _ProductFamily_.NotSet
    data_ = None
    if data_idxs:
      data_ = bytes(data[i] for i in data_idxs)
    elif data is not None:
      data_ = data
    if data_:
      data_bms, data_cfg0 = data_
      pfam = _productfamily_.codec.decode([data_cfg0])
    mask = [255, 0]
    if (
        pfam is _ProductFamily_.Bs8SiMaster
        or pfam - _ProductFamily_.Bsx7 <= 4
        or pfam is _ProductFamily_.SiGsmDn
    ):
      if value == 0:
        bms = _C_.BMS_ZEROVALUE
      elif value == _C_.BMS_ZEROVALUE:
        raise ValueError(
            'invalid value; '
            'expected value is in range(0, 255)'
        )
      else:
        bms = value
    elif value != _C_.BMS_DEFAULT:
      raise ValueError(
          'invalid value; '
          'expected value is 255'
      )
    enc_data = (
      _integer_.Int8u.encode(bms)
      + _productfamily_.codec.encode(pfam)
    )
    return _MaskedData_(enc_data, mask)
  #keep _C_
  #keep _integer_
  #keep _MaskedData_
  #keep _productfamily_
  #keep _ProductFamily_


codec = BackupMemorySizeCodec


del _Codec_
