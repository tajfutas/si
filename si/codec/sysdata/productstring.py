import re as _re_

from si.utils import bitmask as _bitmask_
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
class ProductStringCodec(_Codec_):

  bitsize = 56

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    cfg0, cfg1, cfg2, bn3, bn2, bn1, bn0 = data
    pfam = _productfamily_.codec.decode([cfg0])
    bustype = _bustype_.codec.decode([cfg2])
    sn = _serialnumber_.codec.decode([bn3, bn2, bn1, bn0])
    flag = (cfg0 & 0b10000000 == 0b10000000)
    flag2 = (cfg1 & 0b00100000 == 0b00100000)
    flag3 = (cfg1 & 0b00010000 == 0b00010000)
    flag4 = (cfg1 & 0b00001000 == 0b00001000)
    flag5 = (cfg1 & 0b00000100 == 0b00000100)
    flag6 = (cfg1 & 0b00000010 == 0b00000010)
    text = ''
    text2 = ''
    text3 = ''
    text4 = ''
    if pfam is _product_.ProductFamily.SimSrr:
      text = "SRR"
      text2 = ({
          111: " AP (Dongle)",
          107: " ED_LDK (BS)",
          106: " ED_AH (ActiveCard)"
      }).get(cfg1, "")
      flag6 = False
    elif pfam is _product_.ProductFamily.Bs8SiMaster:
      num = cfg0 & 0b00001111
      text = f"BS{('M' if flag else 'F')}{num}"
      text4 += " Master"
    elif pfam in (
        _product_.ProductFamily.Bsx7,
        _product_.ProductFamily.Bsx8,
    ):
      num = cfg0 & 0b00001111
      text2 = ("-P" if flag2 else "")
      text2 += (("S" if text2 else "-S") if flag5 else "")
      if flag3 or flag4:
        text4 = " UART"
        if flag4:
          text4 += "0"
          text4 += {
              0b00000110: " (USB)",
              0b00000101: " (RS232)",
          }[cfg2 & 0b00000111]
        if flag3:
          text4 += (" + UART1" if flag4 else "1")
          text4 += {
              0b00110000: " (USB)",
              0b00101000: " (RS232)",
          }[cfg2 & 0b00111000]
        if (
            pfam is _product_.ProductFamily.Bsx8
            and cfg1 == 145
            and cfg2 & 0b00111000 != 0b00110000
        ):
          text4 = " UART1 (SRR)"
          flag = False
      else:
        flag = False
      text = f"BS{('M' if flag else 'F')}{num}"
    elif pfam is _product_.ProductFamily.Bs11LoopAntenna:
      text = "BS11 loop antenna"
    elif pfam is _product_.ProductFamily.Bs11Large:
      text = "BS11 large"
    elif pfam is _product_.ProductFamily.Bs11Small:
      text = "BS11 small"
      if sn in _product_.BS11_LOOP_ANTENNA_SN:
        text = "BS11 loop antenna"
    elif pfam is _product_.ProductFamily.SiGsmDn:
      text = "SI-GSMDN"
      flag6 = False
    elif pfam is _product_.ProductFamily.SiPoint:
      d = {144: "SI-Point Golf", 146: "SI-Point SPORTident"}
      text = d.get(cfg1, "SI-Point")
    return (
        f'{text}{text2}{text3}'
        f'{(" RFMOD" if flag6 else "")}'
        f'{text4}'
    )
  #keep _bustype_
  #keep _product_
  #keep _productfamily_
  #keep _serialnumber_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, s, *,
      cfg1=None, cfg2=None, sn=None,
      data=None, data_idxs=None):
    pfam = _product_.ProductFamily.NotSet
    data_ = None
    flag = tuple(128>>i for i in range(8))
    mask = [0] * (cls.bitsize // 8)
    product_cfg1 = None
    product_default_cfg1 = None
    mask[0] = 255
    if cfg1 is not None:
      mask[1] = 255
    if cfg2 is not None:
      mask[2] = 255
    if sn is not None:
      mask[3:7] = [255, 255, 255, 255]
    if data_idxs:
      data_ = bytes(data[i] for i in data_idxs)
    elif data is not None:
      data_ = data
    if data_ is None:
      # set default values
      if cfg1 is None:
        cfg1 = 0  # assumption
        mask[1] |= 255
      if cfg2 is None:
        cfg2 = 255  # assumption
        mask[2] |= 255
    else:
      assert len(data_) == 7
      data_cfg0, data_cfg1, data_cfg2 = data_[:3]
      data_sn = _serialnumber_.codec.decode(data_[3:])
      if cfg1 is None:
        cfg1 = data_cfg1
      if cfg2 is None:
        cfg2 = data_cfg2
      if sn is None:
        sn = data_sn
    bsxre = (r'^BS(?P<mf>[MF])(?P<num>[78])(?:-(?=[PS]))?'
      r'(?P<printout>P)?(?P<sprint>S)?(?:\s(?P<rfmod>RFMOD))?'
      r'(?:\s(?P<uart>(?:UART0 \((?:USB|RS232)\)'
      r' \+ UART1 \((?:USB|RS232)\))'
      r'|(?:UART[01] \((?:USB|RS232)\))))?$')
    bsxre_m = _re_.search(bsxre, s)
    if bsxre_m is not None:
      uart = bsxre_m.group('uart') or ''
      cfg0 = 151 + int(bsxre_m.group('num')) - 7
      pfam = _productfamily_.codec.decode([cfg0])
      if not cfg1:  # set default cfg1 if no cfg1 is set
        cfg1 = flag[0] + flag[7]  # assumption
        mask[1] |= flag[0] + flag[7]
      cfg1 |= flag[2] * bool(bsxre_m.group('printout'))
      cfg1 |= flag[3] * bool('UART1' in uart)
      cfg1 |= flag[4] * bool('UART0' in uart)
      cfg1 |= flag[5] * bool(bsxre_m.group('sprint'))
      mask[1] |= sum(flag[2:6])
      cfg2 |= 0b00111111  # set the last 6 bits on
      mask[2] += 0b00111111
      uartre = r'UART([01]) \((.+?)\)'
      busval = {'USB': 0b00000110, 'RS232': 0b00000101}
      for uartnum, bus in _re_.findall(uartre, uart):
        uartnum = int(uartnum)
        cfg2 -= 0b00000111 << 3 * uartnum
        cfg2 += busval[bus] << 3 * uartnum
    elif _re_.match(r'^BSM8 (?:RFMOD )?Master$', s):
      pfam = _product_.ProductFamily.Bs8SiMaster
      product_default_cfg1 = 129
    elif s == "BSM8 UART1 (SRR)":
      pfam = _product_.ProductFamily.Bsx8
      product_cfg1 = 145
      if cfg2 & 0b00111000 == 0b00110000:
        raise ValueError(
          f'invalid CFG2: {cfg2} (0b{cfg2:0>8b}); '
          'expected anything else than 110 for the [2:5] bits'
        )
    elif s == "SRR":
      pfam = _product_.ProductFamily.SimSrr
      if cfg1 in (106, 107, 111):
        curr_s = cls.decode(data_)
        raise ValueError(
            f'invalid CFG1: {cfg1}; '
            'expected anything else than 106, 107, 111'
        )
    elif s == "SRR AP (Dongle)":
      pfam = _product_.ProductFamily.SimSrr
      product_cfg1 = 111
    elif s == "SRR ED_LDK (BS)":
      pfam = _product_.ProductFamily.SimSrr
      product_cfg1 = 107
    elif s == "SRR ED_AH (ActiveCard)":
      pfam = _product_.ProductFamily.SimSrr
      product_cfg1 = 106
    elif _re_.match(r'^BS11 loop antenna(?: RFMOD)?$', s):
      if sn in _product_.BS11_LOOP_ANTENNA_SN:
        pfam = _product_.ProductFamily.Bs11Small
        product_default_cfg1 = 205
      else:
        pfam = _product_.ProductFamily.Bs11LoopAntenna
        product_default_cfg1 = 145
    elif _re_.match(r'^BS11 large(?: RFMOD)?$', s):
      pfam = _product_.ProductFamily.Bs11Large
      product_default_cfg1 = 157
    elif _re_.match(r'^BS11 small(?: RFMOD)?$', s):
      pfam = _product_.ProductFamily.Bs11Small
      product_default_cfg1 = 205
    elif s == "SI-GSMDN":
      pfam = _product_.ProductFamily.SiGsmDn
      product_default_cfg1 = 27
    elif s == "SI-Point Golf":
      pfam = _product_.ProductFamily.SiPoint
      product_cfg1 = 144
      mask[:2] = [255, 255]
    elif s == "SI-Point":
      pfam = _product_.ProductFamily.SiPoint
      if cfg1 in (144, 146):
        raise ValueError(
            f'invalid CFG1: {cfg1}; '
            'expected anything else than 144, 146'
        )
    elif s == "SI-Point SPORTident RFMOD":
      pfam = _product_.ProductFamily.SiPoint
      product_cfg1 = 146
    else:
      raise NotImplementedError('unsupported product')
    if product_cfg1:
      cfg1 = product_cfg1
      mask[1] = 255
    elif not cfg1 and product_default_cfg1:
      cfg1 = product_default_cfg1
      mask[1] = 255
    if ('RFMOD' in s):
      cfg1 |= flag[6]
      mask[1] |= flag[6]
    enc_data = (
        bytes([pfam, cfg1, cfg2])
        + _serialnumber_.codec.encode(sn)
    )
    return _MaskedData_(enc_data, mask)
  #keep _Codec_
  #keep _MaskedData_
  #keep _product_
  #keep _productfamily_
  #keep _serialnumber_
  #keep _re_


codec = ProductStringCodec


del _enum_
