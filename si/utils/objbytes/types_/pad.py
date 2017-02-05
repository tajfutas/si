#TODO: docstring

from .. import base


class PadBit(base.Bits):
  # TODO: docstring

  _bitsize = 0o1

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


def PadBits(bitsize):
  # TODO: docstring
  if bitsize == 1:
    return PadBit
  else:
    return PadBit.new_subtype('PadBits', _bitsize=bitsize)


del base
