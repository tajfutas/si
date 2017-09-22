import collections as _collections_

from si.codec import enum as _enum_
from si.protocol import \
    BaseRawInstruction as _BaseRawInstruction_
from si.protocol.legacy import Cmd as _Cmd_


class LegacyRawInstruction(_BaseRawInstruction_):

  CMDByte = _enum_.EnumCodec.classfactory(
    'CMDByte',
    enum = _Cmd_,
  )

  Parts = _collections_.namedtuple(
    'LegacyRawInstructionParts',
    ('wakeup', 'stx', 'cmd', 'data', 'etx')
  )

  #TODO encode/decode methods


codec = LegacyRawInstruction


del _BaseRawInstruction_
del _Cmd_
del _collections_
del _enum_
