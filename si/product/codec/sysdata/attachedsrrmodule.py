from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.product import \
  ProductFamily as _ProductFamily_
from . import _constant as _C_
from . import bustype as _bustype_
from . import productfamily as _productfamily_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3073; #L3653-3855)
class AttachedSrrModuleCodec(_Codec_):

  bitsize = 24

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    cfg0, cfg1, cfg2 = data
    pfam = _productfamily_.codec.decode([cfg0])
    bustype = _bustype_.codec.decode([cfg2])
    if (
        pfam is _ProductFamily_.Bsx8
        and cfg1 == _C_.CFG1_BSM
        and bustype & _C_.CFG2_UART1_MASK != _C_.CFG2_UART1_USB
    ):
      return True
    else:
      return False
  #keep _bustype_
  #keep _C_
  #keep _productfamily_
  #keep _ProductFamily_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, attachedsrrmodule, *,
      data=None, data_idxs=None):
    a_pfam = _ProductFamily_.Bsx8
    a_cfg1 = _C_.CFG1_BSM
    bustype = _C_.CFG2_DEFAULT & (255 - _C_.CFG2_UART1_MASK)
    if attachedsrrmodule:
      pfam = a_pfam
      cfg1 = a_cfg1
      bustype += _C_.CFG2_UART1_SRR
    else:
      pfam = _ProductFamily_.NotSet
      cfg1 = _C_.CFG1_DEFAULT
      bustype += _C_.CFG2_UART1_USB
    mask = [255, 255, 255]
    data_ = None
    if data_idxs:
      data_ = bytes(data[i] for i in data_idxs)
    elif data is not None:
      data_ = data
    if data_:
      data_cfg0, data_cfg1, data_cfg2 = data_
      data_pfam = _productfamily_.codec.decode([data_cfg0])
      data_bustype = _bustype_.codec.decode([data_cfg2])
      data_asrrm = (
          data_bustype & _C_.CFG2_UART1_MASK
          != _C_.CFG2_UART1_USB
      )
      mask[2] = (_C_.CFG2_UART1_MASK if data_bustype else 255)
      if data_bustype and data_asrrm == attachedsrrmodule:
        bustype = data_bustype
      if attachedsrrmodule:
        if data_pfam and data_cfg1:
          if data_pfam is not pfam:
            raise ValueError(
                f'unsupported ProductFamily: {data_pfam.name}; '
                f'expected: {pfam.name}; '
                f'hint: set ProductType to Bsm8 first'
            )
          if data_cfg1 != cfg1:
            raise ValueError(
                f'unsupported CFG1: {data_cfg1}; '
                f'expected: {cfg1}; '
                f'hint: set ProductType to Bsm8 first'
            )
      else:
        mask[0:2] = [0, 0]
        if data_pfam is not a_pfam or data_cfg1 != a_cfg1:
          # nothing to do
          mask[2] = [0]
    enc_data = (
      _productfamily_.codec.encode(pfam)
      + bytes([cfg1])
      + _bustype_.codec.encode(bustype)
    )
    return _MaskedData_(enc_data, mask)
  #keep _bustype_
  #keep _C_
  #keep _MaskedData_
  #keep _productfamily_
  #keep _ProductFamily_


codec = AttachedSrrModuleCodec


del _Codec_
