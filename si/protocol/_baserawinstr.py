from si.codec import Codec as _Codec_
from si.codec import constant as _constant_
from si.protocol import ProtoChar as _ProtoChar_


class BaseRawInstruction(_Codec_):

  WAKEUPByte = _constant_.ConstantCodec.classfactory(
    'WAKEUPByte',
    data=_ProtoChar_.WAKEUP.value,
  )

  STXByte = _constant_.ConstantCodec.classfactory(
    'STXByte',
    data=_ProtoChar_.STX.value,
  )

  ETXByte = _constant_.ConstantCodec.classfactory(
    'ETXByte',
    data=_ProtoChar_.ETX.value,
  )


del _Codec_
del _constant_
del _ProtoChar_
