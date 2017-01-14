from enum import Enum
import types
import typing


from si.helper import classproperty, coroutine
from .. import Protocol
from ..helper import get_protocol_from_cmd
from . import Cmd, ProtoChar


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
  CRC: typing.Union[bytes, bytearray]
  ETX: typing.Union[bytes, bytearray]


class Instruction(bytes):
  CMD = NotImplemented
  TYPE = NotImplemented

  _members = {}

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    if cls.CMD != NotImplemented:
      cls._members[cls.CMD] = cls

  @classproperty
  def members(cls):
    return types.MappingProxyType(cls._members)

  @classmethod
  def consumer_factory(cls) -> 'coroutine function':
    @coroutine
    def consumer(cls
      ) -> StopIteration(InstructionConsumerResult):
      state = 'start'
      while True:
        data = (yield)
    # TODO: this is an example oroutine function;
    #   should be replaced with InstructionConsumer (see below)
    return consumer

  @classmethod
  def protocol(self) -> Protocol:
    """
    Return si.communication.Protocol based on the command byte
    """
    if cls.CMD == NotImplemented:
      return Protocol.NotSet
    else:
      return get_protocol_from_cmd(cls.CMD)


class Command(Instruction):
  TYPE = 'command'
  _members = {}


class Response(Instruction):
  TYPE = 'response'
  _members = {}



class InstructionConsumerResult(typing.NamedTuple):
  instruction: Instruction
  remaining_bytes: bytes


class InstructionFactory:

  def __init__(self, data=None):
    self.reset()
    if data:
      self.send(data)

  def __getitem__(self, instrutionpart):
    if hasattr(instrutionpart, 'name'):
      instrutionpart = instrutionpart.name
    try:
      return getattr(self._parts, instrutionpart)
    except AttributeError:
      raise KeyError(instrutionpart) from None

  @property
  def buffer(self):
      return b''.join(self._parts) + self._extra_buffer

  @property
  def parts(self):
      return self._parts

  @coroutine
  def _coro(self):
    while True:
      bytes_ = yield
      self.buffer.extend(bytes_)
      if bytes_ == b'\x00':
        return 'Hello'

  def reset(self, clear_buffer=True):
    self.state = InstructionPart.FF
    self.protocol = Protocol.NotSet
    if clear_buffer:
      self._parts = InstructionParts(
          *(bytearray() for _ in InstructionParts._fields))
      self._extra_buffer = bytearray()
    self.coro=self._coro()

  def send(self, bytes_):
    if bytes_:
      state_name = self.state.name.lower()
      method_name = 'send_at_{}'.format(state_name)
      method = getattr(self, method_name)
      return method(bytes_)
    #self.coro.send(bytes_)

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
      raise ValueError(('invalid protocol byte '
          'received at STX state: {:0>2X}').format(b[0]))
    else:
      self.state = InstructionPart.CMD
      self.send(bytes_)

  def send_at_cmd(self, bytes_):
    b = bytes_[:1]
    try:
      cmd = Cmd(b)
    except ValueError:
      raise ValueError(('invalid protocol byte '
          'received at CMD state: {:0>2X}').format(b[0]))
    self[InstructionPart.CMD].extend(b)
    self.protocol = get_protocol_from_cmd(cmd)
    if self.protocol == Protocol.Legacy:
      self.state = InstructionPart.DATA
    elif self.protocol == Protocol.Extended:
      self.state = InstructionPart.LEN
    self.send(bytes_[1:])


  # TODO: Implement InstructionConsumer with coroutine API;
  #   goal is to provide intermediate data in a bytearray at any
  #   time
