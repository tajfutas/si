import struct as _struct
import sys as _sys

from .. import base


class Integer(base.Base):

  _typecodes = {
      (True, 0o10): 'b',
      (False, 0o10): 'B',
      (True, 0o20): 'h',
      (False, 0o20): 'H',
      (True, 0o40): 'l',
      (False, 0o40): 'L',
      (True, 0o100): 'q',
      (False, 0o100): 'Q',
    }

  def __init__(self, bitsize, *args, signed=True, byteorder=None,
      **kwgs):
    self._params = {'bitsize': bitsize, '*args': args, 'signed': signed}
    self._bitsize = bitsize
    self._signed = signed
    if byteorder is None:
      self._byteorder = _sys.byteorder
    else:
      # TODO: validation
      assert byteorder in ('little', 'big')
      self._byteorder = byteorder
    typecode = self._typecodes.get((signed, bitsize))
    if typecode:
      if self._byteorder == 'little':
        typecode = '<' + typecode
      else:
        typecode = '>' + typecode
    self._typecode = typecode
    super().__init__(bitsize, *args, signed=signed, byteorder=byteorder, **kwgs)

  def _decode(self):
    if self._typecode:
      dat = _struct.pack(self._typecode, self._obj)
    else:
      raise NotImplementedError()
    obj = _struct.unpack(self._typecode, self._dat)[0]
    self._obj = obj
    self._setup |= 0b01

  def _encode(self):
    if self._typecode:
      dat = _struct.pack(self._typecode, self._obj)
    else:
      raise NotImplementedError()
    if self._setup & 0b10:
      self._dat[:] = dat
    else:
      if not self._readonly:
        dat = bytearray(dat)
      self._dat = dat
      self._setup |= 0b10


del base
