import datetime as _datetime_

from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.codec import time as _time_
from si.product import \
  ProductFamily as _ProductFamily_
from . import productfamily as _productfamily_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3105-3120)
class BatteryDateCodec(_Codec_):

  bitsize = 32

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    yy, mm, dd, cfg0 = data
    pfam = _productfamily_.codec.decode([cfg0])
    if (
        pfam is _ProductFamily_.Bs8SiMaster
        or pfam - _ProductFamily_.Bsx7 <= 4
        or pfam is _ProductFamily_.SiGsmDn
    ):
      return _time_.DateCodec.decode(data[0:3])
  #keep _datetime_
  #keep _productfamily_
  #keep _ProductFamily_
  #keep _time_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, *obj,
      data=None, data_idxs=None):
    assert (0<= len(obj) < 2)
    obj = (None if not obj else obj[0])
    pfam = _ProductFamily_.NotSet
    data_ = None
    if data_idxs:
      data_ = bytes(data[i] for i in data_idxs)
    elif data is not None:
      data_ = data
    if data_:
      yy, mm, dd, cfg0 = data_
      pfam = _productfamily_.codec.decode([cfg0])
    if (
        pfam is _ProductFamily_.Bs8SiMaster
        or pfam - _ProductFamily_.Bsx7 <= 4
        or pfam is _ProductFamily_.SiGsmDn
    ):
      enc_data = (
          _time_.DateCodec.encode(obj)
          + _productfamily_.codec.encode(pfam)
      )
      mask = [255, 255, 255, 0]
      return _MaskedData_(enc_data, mask)
    elif obj is not None:
      raise TypeError(
          'invalid date; '
          'expected None value or different ProductFamily'
      )
  #keep _MaskedData_
  #keep _productfamily_
  #keep _ProductFamily_
  #keep _time_


codec = BatteryDateCodec


del _Codec_
