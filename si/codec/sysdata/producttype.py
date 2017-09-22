from si.utils import enumhelper as _enumhelper_
from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.codec import enum as _enum_
from . import bustype as _bustype_
from . import productfamily as _productfamily_
from . import serialnumber as _serialnumber_
from . import __product as _product_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3052; #L3653-3855)
class ProductTypeCodec(_Codec_):

  bitsize = 56

  _pfam2ptype = {
    _product_.ProductFamily.SimSrr:
        _product_.ProductType.SimSrr,
    _product_.ProductFamily.Bs8SiMaster:
        _product_.ProductType.Bs8SiMaster,
    _product_.ProductFamily.Bs11LoopAntenna:
        _product_.ProductType.Bs11LoopAntenna,
    _product_.ProductFamily.Bs11Large:
        _product_.ProductType.Bs11Large,
    _product_.ProductFamily.SiGsmDn:
        _product_.ProductType.SiGsmDn,
    (_product_.ProductFamily.SiPoint, 144):
        _product_.ProductType.SiPointGolf,
    (_product_.ProductFamily.SiPoint, 146):
         _product_.ProductType.SiPointSportident,
    (_product_.ProductFamily.Bsx7, 145):
        _product_.ProductType.Bsm7,
    (_product_.ProductFamily.Bsx7, 129):
        _product_.ProductType.Bsf7,
    (_product_.ProductFamily.Bsx7, 177):
        _product_.ProductType.Bs7P,
    (_product_.ProductFamily.Bsx7, 149):
        _product_.ProductType.Bs7S,
    (_product_.ProductFamily.Bsx8, 129):
        _product_.ProductType.Bsf8,
  }
  _ptype2pfam = {t:f for f, t in _pfam2ptype.items()}
  del _ptype2pfam[_product_.ProductType.Bs11LoopAntenna]
  del _ptype2pfam[_product_.ProductType.Bsf8]
  _cfg1_pfams = {k[0] for k in _pfam2ptype if type(k) is tuple}
  _special_pfams = {
      _product_.ProductFamily.Bsx8,
      _product_.ProductFamily.Bs11Small,
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
    if pfam is _product_.ProductFamily.Bsx8 and cfg1 == 145:
      if bustype & 0b00111000 == 0b00110000:
        return _product_.ProductType.Bsm8
      else:
        return _product_.ProductType.Bsf8
    if pfam is _product_.ProductFamily.Bs11Small:
      if sn in _product_.BS11_LOOP_ANTENNA_SN:
        return _product_.ProductType.Bs11LoopAntenna
      else:
        return _product_.ProductType.Bs11Small
    raise NotImplementedError('unsupported product')
  #keep _bustype_
  #keep _product_
  #keep _productfamily_
  #keep _serialnumber_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, ptype, *,
      attachedsrrmodule=None, sn=None,
      data=None, data_idxs=None):
    pfam = None
    cfg1 = None
    data_cfg1 = None
    ptype = _enumhelper_.get(_product_.ProductType, ptype)
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
    elif ptype is _product_.ProductType.Bsm8:
      pfam = _product_.ProductFamily.Bsx8
      cfg1 = 145
      # TODO! We assume all CFG2 bits on by default: verify
      bustype = (255 - bustype_mask) + bustype_bsm8
      mask = [255, 255, bustype_mask, 0, 0, 0, 0]
    elif ptype is _product_.ProductType.Bsf8:
      pfam = _product_.ProductFamily.Bsx8
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
    elif ptype is _product_.ProductType.Bs11LoopAntenna:
      if (
          sn is not None
          and sn in _product_.BS11_LOOP_ANTENNA_SN
      ):
        pfam = _product_.ProductFamily.Bs11Small
      else:
        pfam = _product_.ProductFamily.Bs11LoopAntenna
      if sn is None:
        mask = [255, 0, 0, 0, 0, 0, 0]
      else:
        mask = [255, 0, 0, 255, 255, 255, 255]
    elif ptype is _product_.ProductType.Bs11Small:
      if sn:
        assert sn not in _product_.BS11_LOOP_ANTENNA_SN
      pfam = _product_.ProductFamily.Bs11Small
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
  #keep _bustype_
  #keep _Codec_
  #keep _enumhelper_
  #keep _MaskedData_
  #keep _productfamily_
  #keep _product_
  #keep _serialnumber_


codec = ProductTypeCodec


del _enum_
