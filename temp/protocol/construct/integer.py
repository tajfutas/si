import functools as _functools
import math as _math
import struct as _struct
import sys as _sys

from . import base as _base

from si.utils import singleton as _s


class Int(_base.ConstructBase):

  def __init__(self, bitsize, signed, byteorder=_s.NotSet):
    self._bitsize = int(bitsize)
    self.signed = bool(signed)
    self._byteorder = _s.NotSet
    self.byteorder = byteorder
    super().__init__()

  @property
  def byteorder(self):
    return self._byteorder
  @byteorder.setter
  def byteorder(self, value):
    if value is _s.NotSet:
      value = _sys.byteorder
    elif value not in {'little', 'big'}:
      raise ValueError(f'invalid byteorder: {value!r} '
          f'(expected \'little\' or \'big\')')
    self._byteorder = value

  def typecode(self):
    first_char = {'little': '<', 'big': '>'}[self.byteorder]
    typecode_ = 'BHLQ'[int(_math.log(self.bitsize // 8, 2))]
    if self.signed:
      typecode_ = typecode_.lower()
    return first_char + typecode_

  def decode(self):
    return _struct.unpack(self.typecode(), self.bytes)[0]

  def encode(self):
    return _struct.pack(self.typecode(), self.obj)


Int8u  = Int.factory(8, False)
Int8s  = Int.factory(8, True)
Int16sl = Int.factory(16, True, 'little')
Int16ul = Int.factory(16, False, 'little')
Int16sb = Int.factory(16, True, 'big')
Int16ub = Int.factory(16, False, 'big')
Int32sl = Int.factory(32, True, 'little')
Int32ul = Int.factory(32, False, 'little')
Int32sb = Int.factory(32, True, 'big')
Int32ub = Int.factory(32, False, 'big')
Int64sl = Int.factory(64, True, 'little')
Int64ul = Int.factory(64, False, 'little')
Int64sb = Int.factory(64, True, 'big')
Int64ub = Int.factory(64, False, 'big')

del _functools

del _base
