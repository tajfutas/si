#TODO: docstring

from .. import base


class PadBase(base.ObjBytes):
  # TODO: docstring

  def __new__(cls, *args, **kwgs) -> 'cls':
    if not args:
      num_bytes, num_bits = divmod(cls._bitsize, 8)
      num_bytes += bool(num_bits)
      args = bytes(num_bytes),
      kwgs['factory_meth'] = False
    return super().__new__(cls, *args, **kwgs)

  @classmethod
  def from_obj(cls,
      obj: None = None,
    ) -> 'cls':
    """
    Return the instance

    The obj parameter must be None if given, otherwise
    ValueError gets raised.
    """
    if obj is not None:
      raise ValueError('obj must be None')
    return cls()

  @classmethod
  def default(cls) -> 'cls':
    return cls()

  def obj(self) -> None:
    return None


def Pad(bitsize, modes):
  # TODO: docstring
  return PadBase.new_subtype('Pad', _bitsize=bitsize,
      _modes=modes)


class PadBit(PadBase):
  # TODO: docstring

  _bitsize = 0o1
  _modes = frozenset((1,))


def PadBits(bitsize):
  # TODO: docstring
  if bitsize == 1:
    return PadBit
  else:
    return PadBit.new_subtype('PadBits', _bitsize=bitsize)


class PadByte(PadBase):
  # TODO: docstring

  _bitsize = 0o10
  _modes = frozenset((8,))


def PadBytes(bytesize):
  # TODO: docstring
  if bytesize == 1:
    return PadByte
  else:
    return PadByte.new_subtype('PadBytes', _bitsize=8*bytesize)


del base
