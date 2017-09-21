import enum as _enum_

from si.codec.instruction.__protocol import ProtoChar


class Mode(_enum_.Enum):
  NotSet = -1
  Legacy = 0
  Extended = 1


del _enum_
