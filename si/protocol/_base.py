import collections
import types
import typing

from ._helper import bits2str, bytes2str, str2bits, str2bytes


class BaseBytes(bytes):
  _OCTETS = NotImplemented

  def __new__(cls, *args,
      _from: typing.Union[None, bool, str] = None,
      _from_exc: typing.Union[Exception, None] = None,
      _get_octets: typing.Union[None, typing.Callable] = None,
      **kwgs
    ) -> 'cls':
    inst = None
    if (_from in (None, True, 'val')
        and hasattr(cls, 'from_val')):
      try:
        inst = cls.from_val(*args)
      except Exception as e:
        if _from is not None:
          _from_exc = e
      else:
        _from_exc = None
    if (inst is None
        and _from in (None, True, 'str')
        and hasattr(cls, 'from_str')):
      try:
        inst = cls.from_str(*args)
      except Exception as e:
        if _from is not None:
          _from_exc = e
      else:
        _from_exc = None
    if _from_exc:
      raise _from_exc
    if inst is None:
      inst = super().__new__(cls, *args, **kwgs)
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
  def from_str(cls, s: typing.Union[str, typing.io]) -> 'cls':
    """
    Create an instance from a string

    String must contain pairs of hexadecimal characters. Spaces
    are ignored.

    See si.protocol._helper.str2bytes()
    """
    return cls(str2bytes(s, octets=cls._OCTETS), _from=False)


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
  def from_str(cls, s: typing.Union[str, typing.io]) -> 'cls':
    """
    Create an instance from a string or a stream

    Input must contain case "o" and "X" characters only. Spaces
    are ignored.

    See si.protocol._helper.str2bits()
    """
    return cls(str2bits(s, octets=cls._OCTETS), _from=False)

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
  def _bytes_from_items(items):
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

  def __new__(cls, *args,
      _from: typing.Union[None, bool, str] = None,
      _from_exc: typing.Union[Exception, None] = None,
      _get_octets: typing.Union[None, typing.Callable] = None,
      _items: typing.Union[None, types.MappingProxyType] = None,
      **kwgs
    ) -> 'cls':
    inst = None
    if (_from in (None, True, 'items')
        and hasattr(cls, 'from_items')):
      try:
        inst = cls.from_items(*args, **kwgs)
      except Exception as e:
        if _from is not None:
          _from_exc = e
      else:
        _from_exc = None
    if inst is None:
      inst = super().__new__(cls, *args,
          _from = _from,
          _from_exc = _from_exc,
          _get_octets = _get_octets,
          **kwgs)
    if _items:
      inst._items = _items
    elif not hasattr(inst, '_items'):
      inst._items = inst._get_items()
    return inst

  @classmethod
  def from_items(cls,
      _itemseq: typing.Union[None, typing.Sequence[
          typing.Union[None, BaseBytes]]] = None,
      **itms
    ) -> 'cls':
    "Create an instance from items" # TODO more docstring
    if _itemseq is None:
      unknw_k = set(itms.keys()) - set(i[0] for i in cls._ITEMS)
      if unknw_k:
        efs = 'invalid key{}: {}'
        raise AttributeError(efs.format(
            ('s' if len(unknw_k) > 1 else ''),
            ', '.join('{!r}'.format(k)
                for k in sorted(unknw_k))))
    else:
      if itms:
        es = 'either sequence of items or item keywords'
        raise AttributeError(es)
    _items = collections.OrderedDict()
    for i, (item_name, item_cls) in enumerate(cls._ITEMS):
      if _itemseq is not None:
        v = _itemseq[i]
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
    arg = cls._bytes_from_items(_items)
    _items = types.MappingProxyType(_items)
    return cls(arg, _from=False, _items=_items)

  @classmethod
  def from_val(cls,
      val: typing.Collection,
    ) -> 'cls':
    raise NotImplementedError()  # TODO

  def __getitem__(self, item):
    if isinstance(item, str):
      return self.items[item]
    else:
      return super().__getitem__(item)

  @property
  def items(self):
    return self._items

  def _get_items(self):
    return NotImplemented  # TODO

  def _get_octets(self):
    return sum((i.octets() for i in self.items.values()))

  def val(self):
    return collections.OrderedDict((name, (item.val()
        if hasattr(item, 'val') else item))
        for name, item in self.items.items())
