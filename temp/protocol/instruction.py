# TODO

from enum import Enum
import types
import typing


from si.utils.methdeco import classproperty
from .common import Cmd, Protocol, ProtoChar
from .crc import CrcBytes


class InstructionPart(Enum):
  FF = b'\xFF'
  STX = b'\x02'
  CMD = 'cmd'
  LEN = 'len'
  DATA = 'data'
  CRC = 'crc'
  ETX = b'\x03'


class InstructionParts(typing.NamedTuple):
  FF: typing.Union[bytes, bytearray]
  STX: typing.Union[bytes, bytearray]
  CMD: typing.Union[bytes, bytearray]
  LEN: typing.Union[bytes, bytearray]
  DATA: typing.Union[bytes, bytearray]
  CRC: typing.Union[CrcBytes, bytes, bytearray]
  ETX: typing.Union[bytes, bytearray]


class Instruction(bytes):
  CMD = NotImplemented
  TYPE = NotImplemented

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    if cls.CMD != NotImplemented:
      cls._members[cls.CMD] = cls

  def __new__(cls, arg, check_crc=True, _parts=None):
    #TODO: __new__ should return member with same CMD when
    #   _members
    return super().__new__(cls, arg)

  def __init__(self, arg, check_crc=True, _parts=None):
    # TODO: sophisticate
    super().__init__()
    if _parts is None:
      try:
        fact = InstructionSorter(self)
      except StopIteration as e:
        _parts, extra_buffer = e.value
        if extra_buffer:
          raise ValueError('too much bytes') from None
      else:
        raise ValueError('not enough bytes')
    self._parts = _parts
    if check_crc:
      # TODO: document that CrcBytes instance expected
      check_result = self._parts.CRC.check_bytes(
          b''.join(self._parts[2:5]))
      if not check_result:
        raise ValueError('crc check failed')

  #TODO: from_parts classmethod

  @classproperty
  def members(cls):
    return types.MappingProxyType(cls._members)

  @property
  def parts(self):
      return self._parts

  def protocol(self) -> Protocol:
    """
    Return si.communication.Protocol based on the command byte
    """
    return self._parts.CMD[0].protocol


class Command(Instruction):
  TYPE = 'command'
  _members = {}


class Response(Instruction):
  TYPE = 'response'
  _members = {}


class InstructionSorterResult(typing.NamedTuple):
  instructionparts: InstructionParts
  remaining_bytes: bytes


class InstructionSorter:

  def __init__(self, data=None):
    self.reset()
    if data:
      self.send(data)

  def __getitem__(self, instructionpart):
    if hasattr(instructionpart, 'name'):
      instructionpart = instructionpart.name
    try:
      return getattr(self._parts, instructionpart)
    except AttributeError:
      raise KeyError(instructionpart) from None

  @property
  def buffer(self):
      return b''.join(self._parts) + self._extra_buffer

  @property
  def parts(self):
      return self._parts

  def reset(self, clear_buffer=True):
    self.state = InstructionPart.FF
    self.protocol = Protocol.NotSet
    self.dle = False
    if clear_buffer:
      self._parts = InstructionParts(
          *(bytearray() for _ in InstructionParts._fields))
      self._extra_buffer = bytearray()

  def send(self, bytes_):
    if bytes_:
      state_name = self.state.name.lower()
      method_name = 'send_at_{}'.format(state_name)
      method = getattr(self, method_name)
      method(bytes_)

  def send_at_ff(self, bytes_):
    b = bytes_[:1]
    if b == ProtoChar.FF.value:
      self[InstructionPart.FF].extend(b)
      self.state = InstructionPart.STX
      self.send(bytes_[1:])
    else:
      self.state = InstructionPart.STX
      self.send(bytes_)

  def send_at_stx(self, bytes_):
    b = bytes_[:1]
    if b == ProtoChar.STX.value:
      self[InstructionPart.STX].extend(b)
      self.send(bytes_[1:])
    elif not self[InstructionPart.STX]:
      self._extra_buffer.extend(bytes_)
      raise ValueError(('invalid protocol byte received at STX '
          'state: {:0>2X}').format(b[0]))
    else:
      self.state = InstructionPart.CMD
      self.send(bytes_)

  def send_at_cmd(self, bytes_):
    b = bytes_[:1]
    try:
      cmd = Cmd(b)
    except ValueError:
      self._extra_buffer.extend(bytes_)
      raise ValueError(('invalid protocol byte received at CMD '
          'state: {:0>2X}').format(b[0]))
    self[InstructionPart.CMD].extend(b)
    self.protocol = get_protocol_from_cmd(cmd)
    if self.protocol == Protocol.Legacy:
      self.state = InstructionPart.DATA
    elif self.protocol == Protocol.Extended:
      self.state = InstructionPart.LEN
    self.send(bytes_[1:])

  def send_at_len(self, bytes_):
    b = bytes_[:1]
    self[InstructionPart.LEN].extend(b)
    self.state = InstructionPart.DATA
    self.send(bytes_[1:])

  def send_at_data(self, bytes_):
    if self[InstructionPart.LEN]:
      exp_len = self[InstructionPart.LEN][0]
      curr_len = len(self[InstructionPart.DATA])
      num_bytes_needed = max(0, exp_len - curr_len)
      num_bytes_to_data = min(len(bytes_), num_bytes_needed)
      data_bytes = bytes_[:num_bytes_to_data]
      remaining_bytes = bytes_[num_bytes_to_data:]
      if num_bytes_needed == num_bytes_to_data:
        self.state = InstructionPart.CRC
      self[InstructionPart.DATA].extend(data_bytes)
      self.send(remaining_bytes)
    else:
      b = bytes_[:1]
      if (not self.dle and b <= b'\x1F'
          and b != ProtoChar.DLE.value):
        self.state = InstructionPart.ETX
        self.send(bytes_)
      else:
        if not self.dle and b == ProtoChar.DLE.value:
          self.dle = True
        elif self.dle and b >  b'\x1F':
          self._extra_buffer.extend(bytes_)
          raise ValueError(('invalid protocol byte received at '
              'DATA state after DLE: {:0>2X}').format(b[0]))
        else:
          self.dle = False
        self[InstructionPart.DATA].extend(b)
        self.send(bytes_[1:])

  def send_at_crc(self, bytes_):
    exp_len = 2 # TODO: XOR on 1 byte?
    curr_len = len(self[InstructionPart.CRC])
    num_bytes_needed = max(0, exp_len - curr_len)
    num_bytes_to_data = min(len(bytes_), num_bytes_needed)
    data_bytes = bytes_[:num_bytes_to_data]
    remaining_bytes = bytes_[num_bytes_to_data:]
    if num_bytes_needed == num_bytes_to_data:
      self.state = InstructionPart.ETX
    self[InstructionPart.CRC].extend(data_bytes)
    self.send(remaining_bytes)

  def send_at_etx(self, bytes_):
    b = bytes_[:1]
    if b != ProtoChar.ETX.value:
      self._extra_buffer.extend(bytes_)
      raise ValueError(('invalid protocol byte received at ETX '
          'state: {:0>2X}').format(b[0]))
    self[InstructionPart.ETX].extend(b)
    self._extra_buffer.extend(bytes_[1:])
    parts = InstructionParts(*((bytes(p) if i != 5 else CrcBytes(p))
        for i, p in enumerate(self._parts)))
    extra_buffer = bytes(self._extra_buffer)
    self.reset()
    raise StopIteration(InstructionSorterResult(parts,
        extra_buffer))
