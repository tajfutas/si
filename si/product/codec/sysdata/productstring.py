import re as _re_

from si.utils import enumhelper as _enumhelper_
from si.codec import Codec as _Codec_
from si.codec import MaskedData as _MaskedData_
from si.codec import enum as _enum_
from si.product import \
  BS11_LOOP_ANTENNA_SN as _BS11_LOOP_ANTENNA_SN_, \
  ProductFamily as _ProductFamily_
from . import _constant as _C_
from . import bustype as _bustype_
from . import productfamily as _productfamily_
from . import serialnumber as _serialnumber_


# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3045-3073; #L3653-3855)
class ProductStringCodec(_Codec_):

  bitsize = 56

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    cfg1, cfg0, cfg2, bn3, bn2, bn1, bn0 = data
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
    if pfam is _ProductFamily_.SimSrr:
      text = "SRR"
      text2 = ({
          _C_.CFG1_SRR_AP: " AP (Dongle)",
          _C_.CFG1_SRR_ED_LDK: " ED_LDK (BS)",
          _C_.CFG1_SRR_ED_AH: " ED_AH (ActiveCard)"
      }).get(cfg1, "")
      flag6 = False
    elif pfam is _ProductFamily_.Bs8SiMaster:
      num = cfg0 & _C_.CFG0_BOARDNUM_MASK
      text = f"BS{('M' if flag else 'F')}{num}"
      text4 += " Master"
    elif pfam in (_ProductFamily_.Bsx7, _ProductFamily_.Bsx8):
      num = cfg0 & _C_.CFG0_BOARDNUM_MASK
      text2 = ("-P" if flag2 else "")
      text2 += (("S" if text2 else "-S") if flag5 else "")
      if flag3 or flag4:
        text4 = " UART"
        if flag4:
          text4 += "0"
          text4 += ({
              _C_.CFG2_UART0_USB: " (USB)",
              _C_.CFG2_UART0_RS323: " (RS232)",
          }).get(cfg2 & _C_.CFG2_UART0_MASK, "")
        if flag3:
          text4 += (" + UART1" if flag4 else "1")
          text4 += ({
              _C_.CFG2_UART1_USB: " (USB)",
              _C_.CFG2_UART1_RS232: " (RS232)",
          }).get(cfg2 & _C_.CFG2_UART1_MASK, "")
        if (
            pfam is _ProductFamily_.Bsx8
            and cfg1 == _C_.CFG1_BSM
            and cfg2 & _C_.CFG2_UART1_MASK != _C_.CFG2_UART1_USB
        ):
          text4 = " UART1 (SRR)"
          flag = False
      else:
        flag = False
      text = f"BS{('M' if flag else 'F')}{num}"
    elif pfam is _ProductFamily_.Bs11LoopAntenna:
      text = "BS11 loop antenna"
    elif pfam is _ProductFamily_.Bs11Large:
      text = "BS11 large"
    elif pfam is _ProductFamily_.Bs11Small:
      text = "BS11 small"
      if sn in _BS11_LOOP_ANTENNA_SN_:
        text = "BS11 loop antenna"
    elif pfam is _ProductFamily_.SiGsmDn:
      text = "SI-GSMDN"
      flag6 = False
    elif pfam is _ProductFamily_.SiPoint:
      d = {
          _C_.CFG1_POGOLF: "SI-Point Golf",
          _C_.CFG1_POSI: "SI-Point SPORTident",
      }
      text = d.get(cfg1, "SI-Point")
    return (
        f'{text}{text2}{text3}'
        f'{(" RFMOD" if flag6 else "")}'
        f'{text4}'
    )
  #keep _BS11_LOOP_ANTENNA_SN_
  #keep _bustype_
  #keep _C_
  #keep _productfamily_
  #keep _ProductFamily_
  #keep _serialnumber_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, s, *, data=None, data_idxs=None):
    pfam = _ProductFamily_.NotSet
    cfg1 = _C_.CFG1_DEFAULT
    bustype = _C_.CFG2_DEFAULT
    sn = 0
    flag = tuple(128 >> i for i in range(8))
    mask = [0] * (cls.bitsize // 8)
    product_cfg1 = None
    product_default_cfg1 = None
    mask[0:3] = [255, 255, 255]
    data_ = None
    if data_idxs:
      data_ = bytes(data[i] for i in data_idxs)
    elif data is not None:
      data_ = data
    if data_ is not None:
      assert len(data_) == 7
      cfg1, cfg0, cfg2 = data_[:3]
      pfam = _productfamily_.codec.decode([cfg0])
      bustype = _bustype_.codec.decode([cfg2])
      sn = _serialnumber_.codec.decode(data_[3:])
    bsxre = (r'^BS(?P<mf>[MF])(?P<num>[78])(?:-(?=[PS]))?'
      r'(?P<printout>P)?(?P<sprint>S)?(?:\s(?P<rfmod>RFMOD))?'
      r'(?:\s(?P<uart>(?:UART0 \((?:USB|RS232)\)'
      r' \+ UART1 \((?:USB|RS232)\))'
      r'|(?:UART[01] \((?:USB|RS232)\))))?$')
    bsxre_m = _re_.search(bsxre, s)
    if bsxre_m is not None:
      pfam = _productfamily_.codec.decode([cfg0])
      cfg0 = 151 + int(bsxre_m.grosup('num')) - 7
      uart = bsxre_m.group('uart') or ''
      if not cfg1:  # set default cfg1 if no cfg1 is set
        cfg1 = flag[0] + flag[7]  # assumption
        mask[1] |= flag[0] + flag[7]
      cfg1 |= flag[2] * bool(bsxre_m.group('printout'))
      cfg1 |= flag[3] * bool('UART1' in uart)
      cfg1 |= flag[4] * bool('UART0' in uart)
      cfg1 |= flag[5] * bool(bsxre_m.group('sprint'))
      mask[1] |= sum(flag[2:6])
      mask[2] |= _C_.CFG2_UART1_MASK + _C_.CFG2_UART0_MASK
      bustype &= 255 - mask[2]
      bustype += _C_.CFG2_UART1_DEFAULT + _C_.CFG2_UART0_DEFAULT
      uartre = r'UART([01]) \((.+?)\)'
      busval = {
          'USB': _C_.CFG2_UART0_USB,
          'RS232': _C_.CFG2_UART0_RS232,
      }
      for uartnum, bus in _re_.findall(uartre, uart):
        uartnum = int(uartnum)
        bustype -= _C_.CFG2_UART0_MASK << 3 * uartnum
        bustype += busval[bus] << 3 * uartnum
    elif _re_.match(r'^BSM8 (?:RFMOD )?Master$', s):
      pfam = _ProductFamily_.Bs8SiMaster
      product_default_cfg1 = _C_.CFG1_BSF
    elif s == "BSM8 UART1 (SRR)":
      pfam = _ProductFamily_.Bsx8
      product_cfg1 = _C_.CFG1_BSM
      bustype &= 255 -_C_.CFG2_UART1_MASK
      bustype += _C_.CFG2_UART1_SRR
    elif s == "SRR":
      pfam = _ProductFamily_.SimSrr
      srr_cfg1s = (
          _C_.CFG1_SRR_ED_AH,
          _C_.CFG1_SRR_ED_LDK,
          _C_.CFG1_SRR_AP,
      )
      if cfg1 in srr_cfg1s:
        curr_s = cls.decode(data_)
        raise ValueError(
            f'invalid CFG1: {cfg1}; '
            'expected anything else than '
            f'{", ".join(srr_cfg1s)}'
        )
    elif s == "SRR AP (Dongle)":
      pfam = _ProductFamily_.SimSrr
      product_cfg1 = _C_.CFG1_SRR_AP
    elif s == "SRR ED_LDK (BS)":
      pfam = _ProductFamily_.SimSrr
      product_cfg1 = _C_.CFG1_SRR_ED_LDK
    elif s == "SRR ED_AH (ActiveCard)":
      pfam = _ProductFamily_.SimSrr
      product_cfg1 = _C_.CFG1_SRR_ED_AH
    elif _re_.match(r'^BS11 loop antenna(?: RFMOD)?$', s):
      if sn in _BS11_LOOP_ANTENNA_SN_:
        pfam = _ProductFamily_.Bs11Small
        product_default_cfg1 = _C_.CFG1_BS11SMALL
      else:
        pfam = _ProductFamily_.Bs11LoopAntenna
        product_default_cfg1 = _C_.CFG1_BSM
    elif _re_.match(r'^BS11 large(?: RFMOD)?$', s):
      pfam = _ProductFamily_.Bs11Large
      product_default_cfg1 = _C_.CFG1_BS11LARGE
    elif _re_.match(r'^BS11 small(?: RFMOD)?$', s):
      pfam = _ProductFamily_.Bs11Small
      product_default_cfg1 = _C_.CFG1_BS11SMALL
    elif s == "SI-GSMDN":
      pfam = _ProductFamily_.SiGsmDn
      product_default_cfg1 = _C_.CFG1_SIGSMDN
    elif s == "SI-Point Golf":
      pfam = _ProductFamily_.SiPoint
      product_cfg1 = _C_.CFG1_POGOLF
      mask[:2] = [255, 255]
    elif s == "SI-Point":
      pfam = _ProductFamily_.SiPoint
      if cfg1 in (_C_.CFG1_POGOLF, _C_.CFG1_POSI):
        raise ValueError(
            f'invalid CFG1: {cfg1}; '
            'expected anything else than '
            f'{_C_.CFG1_POGOLF}, {_C_.CFG1_POSI}'
        )
    elif s == "SI-Point SPORTident RFMOD":
      pfam = _ProductFamily_.SiPoint
      product_cfg1 = _C_.CFG1_POSI
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
        bytes([pfam, cfg1, bustype])
        + _serialnumber_.codec.encode(sn)
    )
    return _MaskedData_(enc_data, mask)
  #keep _BS11_LOOP_ANTENNA_SN_
  #keep _C_
  #keep _Codec_
  #keep _MaskedData_
  #keep _productfamily_
  #keep _ProductFamily_
  #keep _serialnumber_
  #keep _re_


codec = ProductStringCodec


del _enum_
