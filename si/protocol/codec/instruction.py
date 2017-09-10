import struct as _struct

from .. import common as _proto_common
from . import base as _base
from . import constant as _constant
from . import enum as _enum
from . import integer as _integer

from . import extcommand as _extcommand

from si.utils import singleton as _s


FFByte = _constant.ConstantCodec.classfactory('FFByte',
    data=_proto_common.ProtoChar.FF.value,
  )

STXByte = _constant.ConstantCodec.classfactory('STXByte',
    data=_proto_common.ProtoChar.STX.value,
  )

CMDByte = _enum.EnumCodec.classfactory('CMDByte',
    enum = _proto_common.Cmd,
  )

LENByte = _integer.Int8u

ETXByte = _constant.ConstantCodec.classfactory('ETXByte',
    data=_proto_common.ProtoChar.ETX.value,
  )

class CRCBytes(_base.BaseCodec):

  CRC_POLY = 0x8005
  CRC_BITF = 0x8000

  @classmethod
  def encode(cls, payload_data):
    if len(payload_data) < 2:
      num = 0
    else:
      num = 256 * payload_data[0] + payload_data[1]
      if len(payload_data) > 2:
        i = 3
        while i <= len(payload_data) + 2:
          if i < len(payload_data):
            num2 = 256 * payload_data[i - 1] + payload_data[i]
            i += 1
          else:
            if i == len(payload_data):
              num2 = 256 * payload_data[i - 1]
            else:
              num2 = 0
            i += 2
          for j in range(0, 16):
            test = num & cls.CRC_BITF
            num = num + num & 65535
            if num2 & cls.CRC_BITF:
              num = num + 1 & 65535
            if test:
              num = (num ^ cls.CRC_POLY) & 65535
            num2 += num2 & 65535
          i += 1
    return _struct.pack('>H', num)

  @classmethod
  def decode(cls, crc_bytes, payload_data=None):
    if payload_data is not None:
      assert crc_bytes == cls.encode(payload_data)
    return crc_bytes


class BaseInstruction(_base.BaseCodec): pass

class ExtendedInstruction(BaseInstruction):

  @classmethod
  def decode(cls, instr_data, check_crc=True):
    result = {
        'ff': 0,
        'stx': 0,
        'cmd': _s.NotSet,
        'len_': _s.NotSet,
        'data': _s.NotSet,
        'crc': _s.NotSet,
        'etx': 0,
      }
    i = 0
    while True:
      try:
        FFByte.decode(instr_data[i:i+1])
      except ValueError:
        break
      else:
        result['ff'] += 1
        i += 1
    while True:
      try:
        STXByte.decode(instr_data[i:i+1])
      except ValueError:
        break
      else:
        result['stx'] += 1
        i += 1
    if not result['stx']:
      raise ValueError('invalid instruction; STX missing')
    result['cmd'] = CMDByte.decode(instr_data[i:i+1])
    payload_data = instr_data[i:i+1]
    i += 1
    result['len_'] = LENByte.decode(instr_data[i:i+1])
    payload_data += instr_data[i:i+1]
    i += 1
    result['data'] = instr_data[i:i+result['len_']]
    payload_data += result['data']
    i += result['len_']
    result['crc'] = CRCBytes.decode(instr_data[i:i+2],
        (payload_data if check_crc else None))
    i += 2
    ETXByte.decode(instr_data[i:i+1])
    result['etx'] += 1
    i += 1
    if i < len(instr_data):
      raise ValueError('extra data')
    return result

  @classmethod
  def encode(cls, cmd, *, data=b'', ff=1, stx=1, **kwds):
    assert 0 <= ff
    assert 0 < stx
    result = bytearray()
    payload_data = bytearray()
    for _ in range(ff):
      result.extend(FFByte.encode())
    for _ in range(stx):
      result.extend(STXByte.encode())
    payload_data.extend(CMDByte.encode(cmd))
    payload_data.extend(LENByte.encode(len(data)))
    payload_data.extend(data)
    result.extend(payload_data)
    result.extend(CRCBytes.encode(payload_data))
    result.extend(ETXByte.encode())
    return bytes(result)


def extcommand(cmd):
  if hasattr(cmd, 'name'):
    modulename = cmd.name.lower()
  else:
    modulename = cmd.lower()
  return getattr(_extcommand, modulename).Command
