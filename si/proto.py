from enum import Enum


class Char(Enum):
  STX = b'\x02'
      # Start of text, first byte to be transmitted
  ETX = b'\x03'
      # End of text, last byte to be transmitted
  ACK = b'\x06'
      # Positive handshake return
      # when sent to BSx3..6 with a card inserted, causes beep
      # until SI-card taken out
  NAK = b'\x15'
      # Negative handshake return
  DLE = b'\x10'
      # DeLimiter to be inserted before data characters 00-1F
  WAKEUP = b'\xFF'


class RegisterCommands(type):
  # http://python-3-patterns-idioms-test.readthedocs.io/en/lates
  # t/Metaprogramming.html#example-self-registration-of-subclass
  # es
  def __init__(cls, name, bases, nmspc):
    super().__init__(name, bases, nmspc)
    if not hasattr(cls, '_instrs'):
      cls._instrs = dict()
    cls._instrs[cls.CMD] = cls
    bases_keys = {c.CMD for c in bases if c.CMD in cls._instrs}
    for k in bases_keys:
      del cls._instrs[k]  # Remove base classes
  @property
  def instrs(cls):
    if cls.PROTOCOL == NotImplemented:
      return dict(cls._instrs)
    else:
      return {k: c for k, c in cls._instrs.items()
          if c.PROTOCOL == cls.PROTOCOL}


class Command:
  CMD = NotImplemented
  PROTOCOL = NotImplemented
  TYPE = NotImplemented


class Instruction(Command, metaclass=RegisterCommands):
  TYPE = 'command'

  @classmethod
  def consume(cls):
    raise NotImplementedError(
        'should be defined in child classes'
        )


  @classmethod
  def precv(cls, sinstr, station):
    raise NotImplementedError(
        'should be defined in child classes'
        )

  @classmethod
  def psend(cls, *args, **kwds):
    raise NotImplementedError(
        'should be defined in child classes'
        )

  @classmethod
  def srecv(cls, pinstr, station):
    raise NotImplementedError(
        'should be defined in child classes'
        )

  @classmethod
  def ssend(cls, station, *args, **kwds):
    raise NotImplementedError(
        'should be defined in child classes'
        )


class Response(Command, metaclass=RegisterCommands):
  TYPE = 'response'


class RecordOverflow(Exception):

  def __init__(self, instr, data):
    super().__init__('record (self.record) overflow '
        'with data (self.data)')
    self.record = record
    self.data = data


class Record:

  def send(self, data):
    if not data:
      return
    state_name = self.state.name.lower()
    method_name = 'send_when_{}'.format(state_name)
    method = getattr(self, method_name)
    return method(data)

  def send_when_etx(self, data):
    raise RecordOverflow(self, data)
