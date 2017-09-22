from si.utils import enumhelper as _enumhelper_
from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.codec import enum as _enum_
from si.product import \
  BS11_LOOP_ANTENNA_SN as _BS11_LOOP_ANTENNA_SN_, \
  ProductFamily as _ProductFamily_, \
  ProductType as _ProductType_
from . import bustype as _bustype_
from . import productfamily as _productfamily_
from . import serialnumber as _serialnumber_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3052; #L3653-3855)
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
    (_ProductFamily_.SiPoint, 144):
        _ProductType_.SiPointGolf,
    (_ProductFamily_.SiPoint, 146):
         _ProductType_.SiPointSportident,
    (_ProductFamily_.Bsx7, 145):
        _ProductType_.Bsm7,
    (_ProductFamily_.Bsx7, 129):
        _ProductType_.Bsf7,
    (_ProductFamily_.Bsx7, 177):
        _ProductType_.Bs7P,
    (_ProductFamily_.Bsx7, 149):
        _ProductType_.Bs7S,
    (_ProductFamily_.Bsx8, 129):
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
    cfg0, cfg1, cfg2, bn3, bn2, bn1, bn0 = data
    pfam = _productfamily_.codec.decode([cfg0])
    bustype = _bustype_.codec.decode([cfg2])
    sn = _serialnumber_.codec.decode([bn3, bn2, bn1, bn0])
    if pfam in cls._pfam2ptype:
      return cls._pfam2ptype[pfam]
    if (pfam, cfg1) in cls._pfam2ptype:
      return cls._pfam2ptype[(pfam, cfg1)]
    if pfam is _ProductFamily_.Bsx8 and cfg1 == 145:
      if bustype & 0b00111000 == 0b00110000:
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
  #keep _productfamily_
  #keep _ProductFamily_
  #keep _ProductType_
  #keep _serialnumber_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, ptype, *,
      attachedsrrmodule=None, sn=None,
      data=None, data_idxs=None):
    pfam = None
    cfg1 = None
    data_cfg1 = None
    ptype = _enumhelper_.get(_ProductType_, ptype)
    bustype = 255  # assumption
    bustype_mask = 0b00111000
    bustype_bsm8 = 0b00110000
    bustype_bsm7 = 0b00000000 # TODO! unknown yet
    data_ = None
    if data_idxs:
      data_ = bytes(data[i] for i in data_idxs)
    elif data is not None:
      data_ = data
    if data_ is not None:
      assert len(data_) == 7
      data_cfg1 = data_[1]
      if sn is None:
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
      cfg1 = 145
      # TODO! We assume all CFG2 bits on by default: verify
      bustype = (255 - bustype_mask) + bustype_bsm8
      mask = [255, 255, bustype_mask, 0, 0, 0, 0]
    elif ptype is _ProductType_.Bsf8:
      pfam = _ProductFamily_.Bsx8
      if attachedsrrmodule:
        cfg1 = 145
      elif attachedsrrmodule is False:
        cfg1 = 129
      elif data_cfg1 in (129, 145):
        cfg1 = data_cfg1
      else:
        cfg1 = 129
      if cfg1 == 129:
        mask = [255, 255, 0, 0, 0, 0, 0]
      elif cfg1 == 145:
        # TODO! We assume all CFG2 bits on by default: verify
        bustype = (255 - bustype_mask) + bustype_bsm7
        mask = [255, 255, bustype_mask, 0, 0, 0, 0]
    elif ptype is _ProductType_.Bs11LoopAntenna:
      if (
          sn is not None
          and sn in _BS11_LOOP_ANTENNA_SN_
      ):
        pfam = _ProductFamily_.Bs11Small
      else:
        pfam = _ProductFamily_.Bs11LoopAntenna
      if sn is None:
        mask = [255, 0, 0, 0, 0, 0, 0]
      else:
        mask = [255, 0, 0, 255, 255, 255, 255]
    elif ptype is _ProductType_.Bs11Small:
      if sn:
        assert sn not in _BS11_LOOP_ANTENNA_SN_
      pfam = _ProductFamily_.Bs11Small
      mask = [255, 0, 0, 0, 0, 0, 0]
    else:
      raise NotImplementedError('unsupported product')
    if cfg1 is None:
      cfg1 = 0  # assumption
    if sn is None:
        sn = 0
    else:
      mask[-4:] = [255, 255, 255, 255]
    enc_data = (
      _productfamily_.codec.encode(pfam)
      + bytes([cfg1])
      + _bustype_.codec.encode(bustype)
      + _serialnumber_.codec.encode(sn)
    )
    return _MaskedData_(enc_data, mask)
  #keep _BS11_LOOP_ANTENNA_SN_
  #keep _bustype_
  #keep _Codec_
  #keep _enumhelper_
  #keep _MaskedData_
  #keep _productfamily_
  #keep _ProductFamily_
  #keep _ProductType_
  #keep _serialnumber_


codec = ProductTypeCodec


del _enum_
