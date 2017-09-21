from si.codec import Codec as _Codec_
from si.codec import constant as _constant_
from . import __protocol as _protocol_


class BaseInstruction(_Codec_):

  WAKEUPByte = _constant_.ConstantCodec.classfactory(
    'WAKEUPByte',
    data=_protocol_.ProtoChar.WAKEUP.value,
  )

  STXByte = _constant_.ConstantCodec.classfactory(
    'STXByte',
    data=_protocol_.ProtoChar.STX.value,
  )

  ETXByte = _constant_.ConstantCodec.classfactory(
    'ETXByte',
    data=_protocol_.ProtoChar.ETX.value,
  )


del _Codec_
del _constant_
del _protocol_
