from si.utils import enumhelper as _enumhelper_

from si import station as _station_
from si.codec import Codec as _Codec_
from si.codec import enum as _enum_

from . import bustype as _bustype_
from . import productfamily as _productfamily_
from . import serialnumber as _serialnumber_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3052; #L3653-3855)
class ProductTypeCodec(_Codec_):

  _e_pfam = _station_.ProductFamily
  _e_ptyp = _station_.ProductType

  _pfam2ptype = {
    _e_pfam.SimSrr: _e_ptyp.SimSrr,
    _e_pfam.Bs8SiMaster: _e_ptyp.Bs8SiMaster,
    _e_pfam.Bs11LoopAntenna: _e_ptyp.Bs11LoopAntenna,
    _e_pfam.Bs11Large: _e_ptyp.Bs11Large,
    _e_pfam.SiGsmDn: _e_ptyp.SiGsmDn,
    (_e_pfam.SiPoint, 144): _e_ptyp.SiPointGolf,
    (_e_pfam.SiPoint, 146): _e_ptyp.SiPointSportident,
    (_e_pfam.Bsx7, 145): _e_ptyp.Bsm7,
    (_e_pfam.Bsx7, 129): _e_ptyp.Bsf7,
    (_e_pfam.Bsx7, 177): _e_ptyp.Bs7P,
    (_e_pfam.Bsx7, 149): _e_ptyp.Bs7S,
    (_e_pfam.Bsx8, 129): _e_ptyp.Bsf8,
  }
  _ptype2pfam = {t:f for f, t in _pfam2ptype.items()}
  del _ptype2pfam[_e_ptyp.Bs11LoopAntenna]
  del _ptype2pfam[_e_ptyp.Bsf8]
  _cfg1_pfams = {k[0] for k in _pfam2ptype if type(k) is tuple}
  _special_pfams = {_e_pfam.Bsx8, _e_pfam.Bs11Small}

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    _e_pfam = _station_.ProductFamily
    _e_ptyp = _station_.ProductType
    cfg0, cfg1, cfg2, bn3, bn2, bn1, bn0 = data
    pfam = _productfamily_.codec.decode([cfg0])
    bustype = _bustype_.codec.decode([cfg2])
    sn = _serialnumber_.codec.decode([bn3, bn2, bn1, bn0])
    if pfam in cls._pfam2ptype:
      return cls._pfam2ptype[pfam]
    if (pfam, cfg1) in cls._pfam2ptype:
      return cls._pfam2ptype[(pfam, cfg1)]
    if pfam is _e_pfam.Bsx8 and cfg1 == 145:
      if bustype & 0b00111000 == 0b00110000:
        return _e_ptyp.Bsm8
      else:
        return _e_ptyp.Bsf8
    if pfam is _e_pfam.Bs11Small:
      if sn in _station_.BS11_LOOP_ANTENNA_SN:
        return _e_ptyp.Bs11LoopAntenna
      else:
        return _e_ptyp.Bs11Small
    raise NotImplementedError('unsupported product')
  #keep _bustype_
  #keep _productfamily_
  #keep _serialnumber_
  #keep _station_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, ptype, *,
      attachedsrrmodule=None, sn=None,
      data=None, data_idxs=None):
    pfam = None
    data_cfg1 = None
    _e_pfam = _station_.ProductFamily
    _e_ptyp = _station_.ProductType
    ptype = _enumhelper_.get(_e_ptyp, ptype)
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
    elif ptype is _e_ptyp.Bsm8:
      pfam = _e_pfam.Bsx8
      cfg1 = 145
      # TODO! We assume all CFG2 bits on by default: verify
      bustype = (255 - bustype_mask) + bustype_bsm8
      mask = [255, 255, bustype_mask, 0, 0, 0, 0]
    elif ptype is _e_ptyp.Bsf8:
      pfam = _e_pfam.Bsx8
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
    elif ptype is _e_ptyp.Bs11LoopAntenna:
      if sn is not None and sn in _station_.BS11_LOOP_ANTENNA_SN:
        pfam = _e_pfam.Bs11Small
      else:
        pfam = _e_pfam.Bs11LoopAntenna
      if sn is None:
        mask = [255, 0, 0, 0, 0, 0, 0]
      else:
        mask = [255, 0, 0, 255, 255, 255, 255]
    elif ptype is _e_ptyp.Bs11Small:
      if sn:
        assert sn not in _station_.BS11_LOOP_ANTENNA_SN
      pfam = _e_pfam.Bs11Small
      mask = [255, 0, 0, 0, 0, 0, 0]
    else:
      raise NotImplementedError('unsupported product')
    if cfg1 is None:
      cfg1 = 255
    if bustype is None:
      bustype = 255
    if sn is None:
        sn = _serialnumber_.codec.decode([255, 255, 255, 255])
    else:
      mask[-4:] = [255, 255, 255, 255]
    enc_data = (
      _productfamily_.codec.encode(pfam)
      + bytes([cfg1])
      + _bustype_.codec.encode(bustype)
      + _serialnumber_.codec.encode(sn)
    )
    return _Codec_.MaskedData(enc_data, mask)
  #keep _bustype_
  #keep _Codec_
  #keep _enumhelper_
  #keep _productfamily_
  #keep _station_
  #keep _serialnumber_


  del _e_pfam
  del _e_ptyp


codec = ProductTypeCodec


del _enum_
