import collections as _collections_

from si.codec import enum as _enum_
from si.codec.instruction \
    import BaseInstruction as _BaseInstruction_
from . import __protocol as _protocol_


class LegacyInstruction(_BaseInstruction_):

  CMDByte = _enum_.EnumCodec.classfactory(
    'CMDByte',
    enum = _protocol_.Cmd,
  )

  Parts = _collections_.namedtuple(
    'LegacyInstructionParts',
    ('wakeup', 'stx', 'cmd', 'data', 'etx')
  )

  #TODO encode/decode methods


codec = LegacyInstruction


del _BaseInstruction_
del _collections_
del _enum_
del _protocol_
