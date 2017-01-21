import collections
import typing


def bytes2str(bytes_:bytes,
    space: str = ' ',
  ) -> str:
  """
  Convert a bytes object to string of hexadecimal values

  >>> bytes2str(b'hello world')
  '68 65 6C 6C 6F 20 77 6F 72 6C 64'

  Spaces between values can be turned of by setting the
  space parameter to an empty string.

  >>> bytes2str(b'hello world', space='')
  '68656C6C6F20776F726C64'

  Naturally, other space strings are possible.

  >>> bytes2str(b'hello world', space='_')
  '68_65_6C_6C_6F_20_77_6F_72_6C_64'
  """
  return space.join('{:0>2X}'.format(b) for b in bytes_)


def str2bytes(s: str,
    space: str = ' ',
  ) -> bytes:
  """
  Convert a string of hexadecimal vales to a bytes object

  >>> si.protocol._base.str2bytes(
  ...     '68 65 6C 6C 6F 20 77 6F 72 6C 64')
  b'hello world'

  Spaces are ignored between byte values. The space parameter
  defines the space string (default ' ').

  >>> si.protocol._base.str2bytes(
  ...     '68_65_6C_6C_6F_20_77_6F_72_6C_64', space='_')
  b'hello world'
  """
  def int_gen():
    first_c = ''
    for c in s:
      if c == space:
        continue
      elif not first_c:
        first_c = c
        continue
      else:
        yield int(first_c + c, 16)
        first_c = ''
    else:
      if first_c:
        efs = ('last character without pair: {!r}')
        raise ValueError(efs.format(first_c))
  return bytes(x for x in int_gen())


def bits2str(bytes_: bytes,
    octets: typing.Union[int, None] = None,
    space: str = None,
    chars: typing.Sequence[str] = 'oX',
    from_left: bool = False,
  ) -> str:
  """
  Convert a bytes object to string of bit values.

  >>> bits2str(b'\x0F')
  'ooooXXXX'

  Pad bits can be trimmed by setting an explicit octets value.
  Octets default is the lenght of the bytes in octets.

  >>> bits2str(b'\x0F', octets=6)
  'ooXXXX'

  If octets modulo 8 is zero then spaces are added between the
  bytes. Otherwise no spaces are added. The default behavior
  can be overridden with an explicit space string.

  >>> bits2str(b'\x0F\xaa')
  'ooooXXXX XoXoXoXo'
  >>> bits2str(b'\x0F\xaa', octets=13)
  'oXXXXXoXoXoXo'
  >>> bits2str(b'\x0F\xaa', octets=13, space=' ')
  'oXXXX XoXoXoXo'

  If pad bits are in the right side then they can be trimmed
  by setting from_left parameter to True.

  >>> bits2str(b'\x0F\xaa', octets=13, space='_',
  ...     from_left=True)
  'ooooXXXX_XoXoX'
  """
  if octets is None:
    octets = 8 * len(bytes_)
  if space is None:
    if octets % 8:
      space = ''
    else:
      space = ' '
  gens = reversed, iter
  if from_left:
    gens = iter, reversed
  def bit_gen():
    yield from ((B & 2**i) >> i for B in gens[0](bytes_)
        for i in gens[1](range(8)))
  def char_gen():
    for i, b in enumerate(bit_gen(), 1):
      if octets < i:
        break
      yield chars[b]
      if i < octets and not i % 8:
        yield space
  return ''.join(gens[0](tuple(char_gen())))


class BaseBytes(bytes):
  _OCTETS = NotImplemented

  def __new__(cls, arg, *args,
      _from_val=True, _get_octets=None,
      **kwgs):
    if _from_val and hasattr(cls, 'from_val'):
      try:
        return cls.from_val(arg)
      except:
        pass
    inst = super().__new__(cls, arg, *args, **kwgs)
    if _get_octets:
      inst._get_octets = _get_octets
    inst._check_octets()
    return inst

  def __repr__(self):
    return '{}({})'.format(self.__class__.__name__,
        super().__repr__())

  def _check_octets(self) -> typing.Tuple[int, int, int]:
    """
    Check octets

    Called by __init__ and should raise
    * RuntimeError if cls._OCTETS was given wrong,
    * ValueError if the size by the given value would be wrong.

    Return (num_bytes, exp_num_bytes, exp_num_bits) tuple, which
    is a microoptimalization for subclasses which should define
    their _check_octets() with the following first two lines:
      t_ = super()._check_octets()
      num_bytes, exp_num_bytes, exp_num_bits = t_
    Similarly, _check_octets() in subclasses should return:
      return num_bytes, exp_num_bytes, exp_num_bits
    """
    num_bytes = len(self)
    exp_num_bytes, exp_num_bits = divmod(self.octets(), 8)
    exp_num_bytes += bool(exp_num_bits)
    if exp_num_bytes != num_bytes:
      efs = '{}: invalid length (expected {}): {}'
      raise ValueError(efs.format(self.__class__.__name__,
          exp_num_bytes, num_bytes))
    return num_bytes, exp_num_bytes, exp_num_bits

  def octets(self) -> int:
    "Size in bits"
    if self._OCTETS == NotImplemented:
      efs = '{}: expected an explicit or ... self._OCTETS'
      raise NotImplementedError(efs.format(
          self.__class__.__name__))
    elif self._OCTETS == ...:
      try:
        return self._get_octets()
      except AttributeError:
        efs = '{}: expected a _get_octets() method'
        raise NotImplementedError(efs.format(
            self.__class__.__name__))
    else:
      return self._OCTETS


class Bytes(BaseBytes):

  def __init__(self, *args, **kwgs):
    super().__init__()
    exp_num_bytes, exp_num_bits = divmod(self.octets(), 8)
    if exp_num_bits:
      efs = ('{}: invalid cls._OCTETS for Bytes: modulo 8 ',
          'should have been zero')
      raise RuntimeError(efs.format(self.__class__.__name__))
    if exp_num_bytes != len(self):
      efs = '{}: invalid length (expected {}): {}'
      raise ValueError(efs.format(self.__class__.__name__,
          exp_num_bytes, len(self)))

  def __str__(self):
    return bytes2str(self)

  @classmethod
  def from_str(cls, s: str, space: str = ' ') -> 'cls':
    """
    Create an instance from a string

    String must contain pairs of hexadecimal characters.

    See si.protocol._base.str2bytes()
    """
    return cls(str2bytes(s, space=space), _from_val=False)


  def _check_octets(self) -> typing.Tuple[int, int, int]:
    """
    Check octets

    Called by __init__ and should raise
    * RuntimeError if cls._OCTETS was given wrong,
    * ValueError if the size by the given value would be wrong.

    Return (num_bytes, exp_num_bytes, exp_num_bits) tuple, which
    is a microoptimalization for subclasses which should define
    their _check_octets() with the following first two lines:
      t_ = super()._check_octets()
      num_bytes, exp_num_bytes, exp_num_bits = t_
    """
    t_ = super()._check_octets()
    num_bytes, exp_num_bytes, exp_num_bits = t_
    if exp_num_bits:
      efs = ('{}: invalid cls._OCTETS for Bytes: modulo 8 ',
          'should have been zero')
      raise RuntimeError(efs.format(self.__class__.__name__))
    return num_bytes, exp_num_bytes, exp_num_bits


class Bits(BaseBytes):

  def __str__(self):
    return bits2str(self, self.octets())

  @classmethod
  def from_str(cls, s: str) -> 'cls':
    """
    Create an instance from a string

    String must contain case insensitive "o", "0", "X", and "1"
    characters only. Spaces and underscores are ignored.
    """
    def reversed_intgen():
      bit_vals = []
      for c in reversed(s.lower()):
        if c in ' _':
          continue
        if c in 'o0':
          bit_vals.append(0)
        elif c in 'x1':
          bit_vals.append(2**len(bit_vals))
        else:
          efs = ('expected "o", "0", "X", and "1" characters '
              'instead of: {!r}')
          raise ValueError(efs.format(c))
        if len(bit_vals) == 8:
          yield sum(bit_vals)
          bit_vals = []
      else:
        if bit_vals:
          yield sum(bit_vals)
    if hasattr(cls, '_bits') and len(s) != cls._bits:
      efs = 'expected a string of {} characters instead of: {}'
      raise ValueError(efs.format(cls._bits, len(s)))
    return cls(x for x in reversed(list(reversed_intgen())))

  def _check_octets(self) -> typing.Tuple[int, int, int]:
    """
    Check octets

    Called by __init__ and should raise
    * RuntimeError if cls._OCTETS was given wrong,
    * ValueError if the size by the given value would be wrong.

    Return (num_bytes, exp_num_bytes, exp_num_bits) tuple, which
    is a microoptimalization for subclasses which should define
    their _check_octets() with the following first two lines:
      t_ = super()._check_octets()
      num_bytes, exp_num_bytes, exp_num_bits = t_
    """
    t_ = super()._check_octets()
    num_bytes, exp_num_bytes, exp_num_bits = t_
    if self[0] & 2**8-2**exp_num_bits:
      efs = '{}: expected {} zero bits in the first byte'
      raise ValueError(efs.format(self.__class__.__name__,
          8-exp_num_bits))
    return num_bytes, exp_num_bytes, exp_num_bits


class PadBits(Bits):

  _OCTETS = ...

  def __new__(cls, octets, arg=None):
    if arg is None:
      exp_num_bytes, exp_num_bits = divmod(octets, 8)
      exp_num_bytes += bool(exp_num_bits)
      arg = exp_num_bytes
    inst = super().__new__(cls, arg,
        _get_octets=lambda octets=octets: octets)
    return inst

  def default(self):
    return self

  def val(self):
    return self


class Container(Bytes):

  _OCTETS = ...

  _ITEMS = ()

  @staticmethod
  def bytes_from_items(items):
    if hasattr(items, 'values'):
      gen = items.values()
    else:
      gen = iter(items)
    bytes_, last_byte_val = b'', 0b0
    octets, last_byte_bits = 0o0, 0o0
    for item in gen:
      item_num_bytes, item_num_bits = divmod(item.octets(), 8)
      if item_num_bytes:
        if last_byte_val:
          efs = 'received bytes in bitwise mode: {!r}'
          raise ValueError(efs.format(item))
        else:
          bytes_ += item[:item_num_bytes]
          octets += 8 * item_num_bytes
      if item_num_bits:
        Lb, Ib = last_byte_bits, item_num_bits
        S = shift = Lb + Ib - 8
        B = item[-1] & 2**Ib-2**max(0, S)
        if 0 <= S:
          B >>= S
          bytes_ += bytes((last_byte_val + B,))
          octets += 0o10
          last_byte_val = item[-1] & 2**S-1
          last_byte_val <<= 8-S
          last_byte_bits = S
        else:
          B <<= -S
          last_byte_val += B
          last_byte_bits += Ib
          octets += Ib
    else:
      if last_byte_val:
        raise ValueError('finished in bitwise mode')
    return bytes_

  def __new__(cls,
      itemseq: typing.Union[None, typing.Sequence[
          typing.Union[None, BaseBytes]]] = None,
      **itms
    ) -> 'cls':
    if itemseq is None:
      unknw_k = set(itms.keys()) - set(i[0] for i in cls._ITEMS)
      if unknw_k:
        efs = 'invalid key{}: {}'
        raise AttributeError(efs.format(
            ('s' if len(unknw_k) > 1 else ''),
            ', '.join('{!r}'.format(k)
                for k in sorted(unknw_k))))
    else:
      if itms:
        raise AttributeError('either itemseq or item keywords')
    _items = collections.OrderedDict()
    for i, (item_name, item_cls) in enumerate(cls._ITEMS):
      if itemseq is not None:
        v = itemseq[i]
      else:
        v = itms.get(item_name)
      if v is None:
        try:
          item_inst = item_cls.default()
        except AttributeError:
          efs = 'argument ({})  must be defined explicitely: {}'
          raise TypeError(efs.format(i, item_name)) from None
      else:
        if type(v) == item_cls:
          item_inst = v
        else:
          item_inst = item_cls(v)
      _items[item_name] = item_inst
    arg = cls.bytes_from_items(_items)
    inst = super().__new__(cls, arg)
    inst._items = _items
    return inst

  def __getitem__(self, item):
    if isinstance(item, str):
      return self._items[item]
    else:
      return super().__getitem__(item)

  def items(self):
    return collections.OrderedDict(self._items)

  def _get_octets(self):
    return sum((i.octets() for i in self.items().values()))

  def val(self):
    return collections.OrderedDict((name, (item.val()
        if hasattr(item, 'val') else item))
        for name, item in self.items().items())
