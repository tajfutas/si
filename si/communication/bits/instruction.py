import types

import si.helper


class Instruction(bytearray):
  CMD = NotImplemented
  TYPE = NotImplemented

  _members = {}

  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    if cls.CMD != NotImplemented:
      cls._members[cls.CMD] = cls

  @si.helper.classproperty
  def members(cls):
    return types.MappingProxyType(cls._members)


class Command(Instruction):
  TYPE = 'command'
  _members = {}


class Response(Instruction):
  TYPE = 'response'
  _members = {}
