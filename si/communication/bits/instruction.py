import types
import typing


from si.helper import classproperty, coroutine
from .. import Protocol
from ..helper import get_protocol_from_cmd
from . import Cmd


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


class InstructionConsumer:
  pass

  # TODO: Implement InstructionConsumer with coroutine API;
  #   goal is to provide intermediate data in a bytearray at any
  #   time
