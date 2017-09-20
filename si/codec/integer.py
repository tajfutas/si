import math as _math_
import struct as _struct_
import sys as _sys_

from si.codec import Codec as _Codec_


class RegularIntegerCodec(_Codec_):

  bitsize = NotImplemented
  signed = NotImplemented
  byteorder = _sys_.byteorder

  @classmethod
  def typecode(cls):
    first_char = {'little': '<', 'big': '>'}[cls.byteorder]
    typecode_ = 'BHLQ'[int(_math_.log(cls.bitsize // 8, 2))]
    if cls.signed:
      typecode_ = typecode_.lower()
    return first_char + typecode_
  #keep _math_

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    return _struct_.unpack(cls.typecode(), data)[0]
  #keep _struct_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, obj):
    return _struct_.pack(cls.typecode(), obj)
  #keep _struct_


Int8s = RegularIntegerCodec.classfactory('Int8s',
  bitsize=8,
  signed=True,
)

Int8u = RegularIntegerCodec.classfactory('Int8u',
  bitsize=8,
  signed=False,
)

Int16sl = RegularIntegerCodec.classfactory('Int16sl',
  bitsize=16,
  signed=True,
  byteorder='little',
)

Int16ul = RegularIntegerCodec.classfactory('Int16ul',
  bitsize=16,
  signed=False,
  byteorder='little',
)

Int16sb = RegularIntegerCodec.classfactory('Int16sb',
  bitsize=16,
  signed=True,
  byteorder='big',
)

Int16ub = RegularIntegerCodec.classfactory('Int16ub',
  bitsize=16,
  signed=False,
  byteorder='big',
)

Int32sl = RegularIntegerCodec.classfactory('Int32sl',
  bitsize=32,
  signed=True,
  byteorder='little',
)

Int32ul = RegularIntegerCodec.classfactory('Int32ul',
  bitsize=32,
  signed=False,
  byteorder='little',
)

Int32sb = RegularIntegerCodec.classfactory('Int32sb',
  bitsize=32,
  signed=True,
  byteorder='big',
)

Int32ub = RegularIntegerCodec.classfactory('Int32ub',
  bitsize=32,
  signed=False,
  byteorder='big',
)

Int64sl = RegularIntegerCodec.classfactory('Int64sl',
  bitsize=64,
  signed=True,
  byteorder='little',
)

Int64ul = RegularIntegerCodec.classfactory('Int64ul',
  bitsize=64,
  signed=False,
  byteorder='little',
)

Int64sb = RegularIntegerCodec.classfactory('Int64sb',
  bitsize=64,
  signed=True,
  byteorder='big',
)

Int64ub = RegularIntegerCodec.classfactory('Int64ub',
  bitsize=64,
  signed=False,
  byteorder='big',
)


del _sys_
del _Codec_
