import collections as _collections_

from si import exc as _exc_
from si.utils import singleton as _s_
from si.codec import Codec as _Codec_
from si.codec import enum as _enum_
from si.codec import integer as _integer_
from si.codec.instruction \
    import BaseInstruction as _BaseInstruction_
from . import __protocol as _protocol_

_crc_ = _protocol_.crc


class ExtendedInstruction(_BaseInstruction_):

  CMDByte = _enum_.EnumCodec.classfactory(
    'CMDByte',
    enum = _protocol_.Cmd,
  )

  LENByte = _integer_.Int8u

  class CRCBytes(_Codec_):

    @classmethod
    @_Codec_.decodemethod
    def decode(cls, crc_bytes, payload_data=None):
      # It checks CRC when payload_data is given
      assert len(crc_bytes) == 2
      if payload_data is not None:
        assert crc_bytes == _crc_(payload_data)
      return crc_bytes
    #keep _crc_

    @classmethod
    @_Codec_.encodemethod
    def encode(cls, payload_data):
      return _crc_(payload_data)
    #keep _crc_

  Parts = _collections_.namedtuple(
    'ExtendedInstructionParts',
    ('wakeup', 'stx', 'cmd', 'len', 'data', 'crc', 'etx')
  )

  @classmethod
  def make_obj(cls, cmd, data, *, wakeup=1, stx=1, len_=None,
      crc=None, etx=1, verify_crc=True):
    assert 0 <= wakeup
    assert 0 < stx
    assert 1 == etx
    cmd_byte = cls.CMDByte.encode(cmd)
    cmd = cls.CMDByte.enum(cmd_byte)
    if data is None:
      data = b''
    else:
      data = bytes(data)
    if len_:
      if isinstance(len_, int):
        len_byte = cls.LENByte.encode(len_)
      else:
        len_byte = len_
        len_ = cls.LENByte.decode(len_byte)
      assert len_ == len(data)
    else:
      len_ = len(data)
      len_byte = cls.LENByte.encode(len_)
    if crc is None:
      crc = cls.CRCBytes.encode(cmd_byte + len_byte + data)
    else:
      crc = bytes(crc)
      if verify_crc:
        crc_ = cls.CRCBytes.encode(cmd_byte + len_byte + data)
        if crc != crc_:
          raise _exc_.CRCError()
    return cls.Parts(wakeup, stx, cmd, len_, data, crc, etx)
  #keep _exc_

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data, check_crc_=True):
    params = {
        'wakeup': 0,
        'stx': 0,
        'cmd': _s_.NotSet,
        'len_': _s_.NotSet,
        'data': _s_.NotSet,
        'crc': _s_.NotSet,
        'etx': 0,
      }
    i = 0
    while True:
      try:
        cls.WAKEUPByte.decode(data[i:i+1])
      except ValueError:
        break
      else:
        params['wakeup'] += 1
        i += 1
    while True:
      try:
        cls.STXByte.decode(data[i:i+1])
      except ValueError:
        break
      else:
        params['stx'] += 1
        i += 1
    if not params['stx']:
      raise ValueError('invalid instruction; STX missing')
    params['cmd'] = cls.CMDByte.decode(data[i:i+1])
    payload_data = data[i:i+1]
    i += 1
    params['len_'] = cls.LENByte.decode(data[i:i+1])
    payload_data += data[i:i+1]
    i += 1
    params['data'] = data[i:i+params['len_']]
    payload_data += params['data']
    i += params['len_']
    params['crc'] = cls.CRCBytes.decode(data[i:i+2],
        (payload_data if check_crc_ else None))
    i += 2
    cls.ETXByte.decode(data[i:i+1])
    params['etx'] += 1
    i += 1
    if i < len(data):
      raise ValueError('extra data')
    return cls.make_obj(**params)
  #keep _s_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, obj):
    return bytes(
        cls.WAKEUPByte.encode() * obj.wakeup
        + cls.STXByte.encode() * obj.stx
        + obj.cmd.value
        + cls.LENByte.encode(obj.len)
        + obj.data
        + obj.crc
        + cls.ETXByte.encode() * obj.etx
      )


codec = ExtendedInstruction


del _BaseInstruction_
del _collections_
del _protocol_
del _Codec_
del _enum_
del _integer_
