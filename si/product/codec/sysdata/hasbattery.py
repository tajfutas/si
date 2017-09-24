from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.product import \
  ProductFamily as _ProductFamily_
from . import _constant as _C_
from . import productfamily as _productfamily_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3073; #L3653-3855)
class HasBatteryCodec(_Codec_):

  bitsize = 16

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    cfg1, cfg0 = data
    pfam = _productfamily_.codec.decode([cfg0])
    if (
        (pfam - _ProductFamily_.Bsx8 and cfg1 == _C_.CFG1_BSM)
        or pfam is _ProductFamily_.SimSrr
    ):
      return False
    else:
      return True
  #keep _C_
  #keep _productfamily_
  #keep _ProductFamily_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, value=None):
    if value is not None:
      raise TypeError(
          'unable to set directly; '
          'hint: set ProductType instead'
      )
    else:
      return _MaskedData_(b'\x00\x00', [0, 0])
  #keep _MaskedData_


codec = HasBatteryCodec


del _Codec_
