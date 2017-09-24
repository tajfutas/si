from si.utils import enumhelper as _enumhelper_
from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.codec import enum as _enum_
from si.product import \
  BS11_LOOP_ANTENNA_SN as _BS11_LOOP_ANTENNA_SN_, \
  ProductFamily as _ProductFamily_, \
  ProductType as _ProductType_
from . import _constant as _C_
from . import bustype as _bustype_
from . import productfamily as _productfamily_
from . import serialnumber as _serialnumber_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3073; #L3653-3855)
class ProductTypeCodec(_Codec_):

  bitsize = 56

  _pfam2ptype = {
    _ProductFamily_.SimSrr:
        _ProductType_.SimSrr,
    _ProductFamily_.Bs8SiMaster:
        _ProductType_.Bs8SiMaster,
    _ProductFamily_.Bs11LoopAntenna:
        _ProductType_.Bs11LoopAntenna,
    _ProductFamily_.Bs11Large:
        _ProductType_.Bs11Large,
    _ProductFamily_.SiGsmDn:
        _ProductType_.SiGsmDn,
    (_ProductFamily_.SiPoint, _C_.CFG1_POGOLF):
        _ProductType_.SiPointGolf,
    (_ProductFamily_.SiPoint, _C_.CFG1_POSI):
         _ProductType_.SiPointSportident,
    (_ProductFamily_.Bsx7, _C_.CFG1_BSM):
        _ProductType_.Bsm7,
    (_ProductFamily_.Bsx7, _C_.CFG1_BSF):
        _ProductType_.Bsf7,
    (_ProductFamily_.Bsx7, _C_.CFG1_BSP):
        _ProductType_.Bs7P,
    (_ProductFamily_.Bsx7, _C_.CFG1_BSS):
        _ProductType_.Bs7S,
    (_ProductFamily_.Bsx8, _C_.CFG1_BSF):
        _ProductType_.Bsf8,
  }
  _ptype2pfam = {t:f for f, t in _pfam2ptype.items()}
  del _ptype2pfam[_ProductType_.Bs11LoopAntenna]
  del _ptype2pfam[_ProductType_.Bsf8]
  _cfg1_pfams = {k[0] for k in _pfam2ptype if type(k) is tuple}
  _special_pfams = {
      _ProductFamily_.Bsx8,
      _ProductFamily_.Bs11Small,
  }

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    cfg1, cfg0, cfg2, bn3, bn2, bn1, bn0 = data
    pfam = _productfamily_.codec.decode([cfg0])
    bustype = _bustype_.codec.decode([cfg2])
    sn = _serialnumber_.codec.decode([bn3, bn2, bn1, bn0])
    if pfam in cls._pfam2ptype:
      return cls._pfam2ptype[pfam]
    if (pfam, cfg1) in cls._pfam2ptype:
      return cls._pfam2ptype[(pfam, cfg1)]
    if pfam is _ProductFamily_.Bsx8 and cfg1 == _C_.CFG1_BSM:
      if bustype & _C_.CFG2_UART1_MASK == _C_.CFG2_UART1_USB:
        return _ProductType_.Bsm8
      else:
        return _ProductType_.Bsf8
    if pfam is _ProductFamily_.Bs11Small:
      if sn in _BS11_LOOP_ANTENNA_SN_:
        return _ProductType_.Bs11LoopAntenna
      else:
        return _ProductType_.Bs11Small
    raise NotImplementedError('unsupported product')
  #keep _BS11_LOOP_ANTENNA_SN_
  #keep _bustype_
  #keep _C_
  #keep _productfamily_
  #keep _ProductFamily_
  #keep _ProductType_
  #keep _serialnumber_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, ptype, *, data=None, data_idxs=None):
    ptype = _enumhelper_.get(_ProductType_, ptype)
    pfam = _ProductFamily_.NotSet
    cfg1 = _C_.CFG1_DEFAULT
    bustype = _C_.CFG2_DEFAULT
    sn = 0
    data_ = None
    if data_idxs:
      data_ = bytes(data[i] for i in data_idxs)
    elif data is not None:
      data_ = data
    if data_ is not None:
      assert len(data_) == 7
      cfg1 = data_[0]
      sn = _serialnumber_.codec.decode(data_[-4:])
    if ptype in cls._ptype2pfam:
      ptypematch = cls._ptype2pfam[ptype]
      if type(ptypematch) is tuple:
        pfam, cfg1 = ptypematch
        mask = [255, 255, 0, 0, 0, 0, 0]
      else:
        pfam = ptypematch
        mask = [255, 0, 0, 0, 0, 0, 0]
    elif ptype is _ProductType_.Bsm8:
      pfam = _ProductFamily_.Bsx8
      cfg1 = _C_.CFG1_BSM
      # TODO! We assume all CFG2 bits on by default: verify
      bustype = (255 - _C_.CFG2_UART1_MASK) + _C_.CFG2_UART1_USB
      mask = [255, 255, _C_.CFG2_UART1_MASK, 0, 0, 0, 0]
    elif ptype is _ProductType_.Bsf8:
      pfam = _ProductFamily_.Bsx8
      cfg1 = _C_.CFG1_BSF
      mask = [255, 255, 0, 0, 0, 0, 0]
    elif ptype is _ProductType_.Bs11LoopAntenna:
      if sn in _BS11_LOOP_ANTENNA_SN_:
        pfam = _ProductFamily_.Bs11Small
      else:
        pfam = _ProductFamily_.Bs11LoopAntenna
      mask = [255, 0, 0, 0, 0, 0, 0]
    elif ptype is _ProductType_.Bs11Small:
      assert sn not in _BS11_LOOP_ANTENNA_SN_
      pfam = _ProductFamily_.Bs11Small
      mask = [255, 0, 0, 0, 0, 0, 0]
    else:
      raise NotImplementedError('unsupported product')
    enc_data = (
      _productfamily_.codec.encode(pfam)
      + bytes([cfg1])
      + _bustype_.codec.encode(bustype)
      + _serialnumber_.codec.encode(sn)
    )
    return _MaskedData_(enc_data, mask)
  #keep _BS11_LOOP_ANTENNA_SN_
  #keep _bustype_
  #keep _C_
  #keep _Codec_
  #keep _enumhelper_
  #keep _MaskedData_
  #keep _productfamily_
  #keep _ProductFamily_
  #keep _ProductType_
  #keep _serialnumber_


codec = ProductTypeCodec


del _enum_
