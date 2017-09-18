from si.utils import enumhelper as _enumhelper

from si.protocol import station as _station
from si.protocol.codec import base as _codec
from si.protocol.codec import enum as _enum
from si.protocol.codec import integer as _integer

from . import bustype as _bustype
from . import productfamily as _productfamily
from . import serialnumber as _serialnumber

# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3052; #L3653-3855)
codec = _enum.EnumCodec.classfactory('ProductTypeCodec',
    enum=_station.ProductType, subcodec=_integer.Int16ub)

class ProductTypeCodec(_codec.Codec):

  _e_pfam = _station.ProductFamily
  _e_ptype = _station.ProductType

  _pfam2ptype = {
    _e_pfam.SimSrr: _e_ptype.SimSrr,
    _e_pfam.Bs8SiMaster: _e_ptype.Bs8SiMaster,
    _e_pfam.Bs11LoopAntenna: _e_ptype.Bs11LoopAntenna,
    _e_pfam.Bs11Large: _e_ptype.Bs11Large,
    _e_pfam.SiGsmDn: _e_ptype.SiGsmDn,
    (_e_pfam.SiPoint, 144): _e_ptype.SiPointGolf,
    (_e_pfam.SiPoint, 146): _e_ptype.SiPointSportident,
    (_e_pfam.Bsx7, 145): _e_ptype.Bsm7,
    (_e_pfam.Bsx7, 129): _e_ptype.Bsf7,
    (_e_pfam.Bsx7, 177): _e_ptype.Bs7P,
    (_e_pfam.Bsx7, 149): _e_ptype.Bs7S,
    (_e_pfam.Bsx8, 129): _e_ptype.Bsf8,
  }
  _ptype2pfam = {t:f for f, t in _pfam2ptype.items()}
  del _ptype2pfam[_e_ptype.Bs11LoopAntenna]
  del _ptype2pfam[_e_ptype.Bsf8]
  _cfg1_pfams = {k[0] for k in _pfam2ptype if type(k) is tuple}
  _special_pfams = {_e_pfam.Bsx8, _e_pfam.Bs11Small}

  @classmethod
  @_codec.decodemethod
  def decode(cls, data):
    _e_pfam = _station.ProductFamily
    _e_ptype = _station.ProductType
    cfg0, cfg1, cfg2, bn3, bn2, bn1, bn0 = data
    pfam = _productfamily.codec.decode([cfg0])
    bustype = _bustype.codec.decode([cfg2])
    sn = _serialnumber.codec.decode([bn3, bn2, bn1, bn0])
    if pfam in cls._pfam2ptype:
      return cls._pfam2ptype[pfam]
    if (pfam, cfg1) in cls._pfam2ptype:
      return cls._pfam2ptype[(pfam, cfg1)]
    if pfam is _e_pfam.Bsx8 and cfg1 == 145:
      if bustype & 0b00111000 == 0b00110000:
        return _e_ptype.Bsm8
      else:
        return _e_ptype.Bsf8
    if pfam is _e_pfam.Bs11Small:
      if sn in _station.BS11_LOOP_ANTENNA_SN:
        return _e_ptype.Bs11LoopAntenna
      else:
        return _e_ptype.Bs11Small
    raise NotImplementedError('unsupported product')

  @classmethod
  @_codec.encodemethod
  def encode(cls, ptype, *, cfg1=None, bustype=None,
      sn=None, attachedsrrmodule=None, data=None,
      data_idxs=None):
    pfam = None
    data_cfg1, cfg1_ = None, None
    _e_pfam = _station.ProductFamily
    _e_ptype = _station.ProductType
    ptype = _enumhelper.get(_e_ptype, ptype)
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
        sn = _serialnumber.codec.decode(data_[-4:])
    if ptype in cls._ptype2pfam:
      ptypematch = cls._ptype2pfam[ptype]
      if type(ptypematch) is tuple:
        pfam, cfg1_ = ptypematch
        mask = [255, 255, 0, 0, 0, 0, 0]
      else:
        pfam = ptypematch
        mask = [255, 0, 0, 0, 0, 0, 0]
    elif ptype is _e_ptype.Bsm8:
      pfam = _e_pfam.Bsx8
      cfg1_ = 145
      # TODO! We assume all CFG2 bits on by default: verify
      bustype = (255 - bustype_mask) + bustype_bsm8
      mask = [255, 255, bustype_mask, 0, 0, 0, 0]
    elif ptype is _e_ptype.Bsf8:
      pfam = _e_pfam.Bsx8
      if cfg1 is None:
        if attachedsrrmodule:
          cfg1 = 145
        elif attachedsrrmodule is False:
          cfg1 = 129
        elif data_cfg1 in (129, 145):
          cfg1 = data_cfg1
        else:
          cfg1 = 129
      else:
        assert cfg1 in (129, 145)
      if cfg1 == 129:
        mask = [255, 255, 0, 0, 0, 0, 0]
      elif cfg1 == 145:
        # TODO! We assume all CFG2 bits on by default: verify
        bustype = (255 - bustype_mask) + bustype_bsm7
        mask = [255, 255, bustype_mask, 0, 0, 0, 0]
    elif ptype is _e_ptype.Bs11LoopAntenna:
      if sn is not None and sn in _station.BS11_LOOP_ANTENNA_SN:
        pfam = _e_pfam.Bs11Small
      else:
        pfam = _e_pfam.Bs11LoopAntenna
      if sn is None:
        mask = [255, 0, 0, 0, 0, 0, 0]
      else:
        mask = [255, 0, 0, 255, 255, 255, 255]
    elif ptype is _e_ptype.Bs11Small:
      if sn:
        assert sn not in _station.BS11_LOOP_ANTENNA_SN
      pfam = _e_pfam.Bs11Small
      mask = [255, 0, 0, 0, 0, 0, 0]
    else:
      raise NotImplementedError('unsupported product')
    if cfg1 is None:
      if cfg1_ is None:
        cfg1 = 255
      else:
        cfg1 = cfg1_
    if bustype is None:
      bustype = 255
    if sn is None:
        sn = _serialnumber.codec.decode([255, 255, 255, 255])
    else:
      mask[-4:] = [255, 255, 255, 255]
    enc_data = (
      _productfamily.codec.encode(pfam)
      + bytes([cfg1])
      + _bustype.codec.encode(bustype)
      + _serialnumber.codec.encode(sn)
    )
    return _codec.MaskedData(enc_data, mask)



  del _e_pfam
  del _e_ptype

codec = ProductTypeCodec

del _enum
del _integer
