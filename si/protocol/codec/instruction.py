import collections as _collections
import struct as _struct

from .. import common as _proto_common

from si import exc as _exc
from si.protocol.codec import base as _codec
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


class CRCBytes(_codec.Codec):

  CRC_POLY = 0x8005
  CRC_BITF = 0x8000

  @classmethod
  @_codec.decodemethod
  def decode(cls, crc_bytes, payload_data=None):
    if payload_data is not None:
      assert crc_bytes == cls.encode(payload_data)
    return crc_bytes

  @classmethod
  @_codec.encodemethod
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


class BaseInstruction(_codec.Codec): pass

class ExtendedInstruction(BaseInstruction):

  Parts = _collections.namedtuple(
    'ExtendedInstructionParts',
    ('ff', 'stx', 'cmd', 'len', 'data', 'crc', 'etx')
  )

  @classmethod
  def make_obj(cls, cmd, data, *, ff=1, stx=1, len_=None,
      crc=None, etx=1, verify_crc=True):
    assert 0 <= ff
    assert 0 < stx
    assert 1 == etx
    cmd_byte = CMDByte.encode(cmd)
    cmd = CMDByte.enum(cmd_byte)
    if data is None:
      data = b''
    else:
      data = bytes(data)
    if len_:
      if isinstance(len_, int):
        len_byte = LENByte.encode(len_)
      else:
        len_byte = len_
        len_ = LENByte.decode(len_byte)
      assert len_ == len(data)
    else:
      len_ = len(data)
      len_byte = LENByte.encode(len_)
    if crc is None:
      crc = CRCBytes.encode(cmd_byte + len_byte + data)
    else:
      crc = bytes(crc)
      if verify_crc:
        crc_ = CRCBytes.encode(cmd_byte + len_byte + data)
        if crc != crc_:
          raise exc_.CRCError()
    return cls.Parts(ff, stx, cmd, len_, data, crc, etx)

  @classmethod
  @_codec.decodemethod
  def decode(cls, data, check_crc=True):
    params = {
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
        FFByte.decode(data[i:i+1])
      except ValueError:
        break
      else:
        params['ff'] += 1
        i += 1
    while True:
      try:
        STXByte.decode(data[i:i+1])
      except ValueError:
        break
      else:
        params['stx'] += 1
        i += 1
    if not params['stx']:
      raise ValueError('invalid instruction; STX missing')
    params['cmd'] = CMDByte.decode(data[i:i+1])
    payload_data = data[i:i+1]
    i += 1
    params['len_'] = LENByte.decode(data[i:i+1])
    payload_data += data[i:i+1]
    i += 1
    params['data'] = data[i:i+params['len_']]
    payload_data += params['data']
    i += params['len_']
    params['crc'] = CRCBytes.decode(data[i:i+2],
        (payload_data if check_crc else None))
    i += 2
    ETXByte.decode(data[i:i+1])
    params['etx'] += 1
    i += 1
    if i < len(data):
      raise ValueError('extra data')
    return cls.make_obj(**params)

  @classmethod
  @_codec.encodemethod
  def encode(cls, obj):
    return bytes(
        FFByte.encode() * obj.ff
        + STXByte.encode() * obj.stx
        + obj.cmd.value
        + LENByte.encode(obj.len)
        + obj.data
        + obj.crc
        + ETXByte.encode() * obj.etx
      )


def extcommand(cmd):
  if hasattr(cmd, 'name'):
    modulename = cmd.name.lower()
  else:
    modulename = cmd.lower()
  return getattr(_extcommand, modulename).Command
