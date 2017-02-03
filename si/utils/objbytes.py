"""
This module provides base and utility classes which are all
subclasses of builtin bytes and which are do an automatic
serialization and deserialization of the object they represent.

The module provides base classes which should be subclassed and
customized for each object. See docstring of BaseBytes and the
particular base class for more information.

Base classes:
  * Bytes
  * Bits
  * DictBytes

The module provides some utility classes for the most common
cases. These classes does not have to get subclassed, but a
simple sublass with a pass could be reasonable to assigning a
name to the underlying object.

Utility classes:
  * PadBit
  * PadBits

By default objbytes instances can be made by passing either the
object they should represent or a bytes-like object (which is
checked for having a decode method) containing the data.
In addition, there are other special ways of instantiating and
each of them is represented by a from_something() classmethod.

If the subclass has a default value, then it can be instantiated
by passing no arguments to the class.
"""

import collections as _collections
import io as _io
from types import MappingProxyType as _MappingProxyType
import typing

from . import bconv as _bconv



################################################################
# SUPERCLASS                                                   #
################################################################


class BaseBytes(bytes):
  """
  Superclass of all objbytes classes. Subclass of bytes.
  Every objbytes class should be inherited by this class.

  Subclasses must define the following
  * class constant:
    - _octets: integer or None
      If integer then it is the size of the data in bits.
      None indicates variable size which gets determined during
      instantiation.
  * classmethod:
    - from_obj(obj)
      Does the serialization (conversion to bytes) of the given
      object and return an objbytes instance.
  * method:
    - obj()
      Does the deserialization (conversion from bytes) an return
      the object the objbites instance represent.

  Subclasses may optionally definde the following
  * classmethod:
    - default()
      Return the default instance. Recommended to be defined if
      such an object exist.
  """
  _FROM_ORDER = ('obj',)  # type: typing.Tuple[str]

  _octets = NotImplemented  # type: typing.Union[None, int]

  def __new__(cls, *args,
      _check_octets: bool = True,
      _from: typing.Union[None, bool, str] = None,
      _from_exc: typing.Union[Exception, None] = None,
      _octets: typing.Union[None, int] = None,
      **kwgs
    ) -> 'cls':
    """
    Create a new instance.

    Attention! If first argument is a bytes-like object (has
    'decode' method) then instance creation is delegated to
    builtin bytes. Otherwise it is treated as the serialized
    object the data represent.
    """
    inst = None
    first_arg = args[0] if args else None
    if first_arg is None and not kwgs:
      return cls.default()
    elif hasattr(first_arg, 'decode'): # is bytes-like
      _from = False
    if _from is not False:
      for name in cls._FROM_ORDER:
        attr_name = 'from_{}'.format(name)
        if (inst is None
            and _from in (None, True, name)
            and hasattr(cls, attr_name)):
          try:
            inst = getattr(cls, attr_name)(*args,
                _check_octets = _check_octets,
                _octets = _octets,
                **kwgs)
          except (ValueError, TypeError) as e:
            _from_exc = e
          else:
            _from_exc = None
      if _from is not None and _from_exc:
        raise _from_exc
    if inst is None:
      inst = super().__new__(cls, *args, **kwgs)
    if _octets:
      if cls._octets is not None:
        efs = ('{}: attempt to set instance octets for a fixed '
            'size data')
        raise ValueError(efs.format(cls.__name__))
      inst._octets = _octets
    if _check_octets:
      inst._check_octets()
    return inst

  def __repr__(self):
    return '{}({})'.format(self.__class__.__name__,
        super().__repr__())

  def __str__(self):
    return _bconv.ints2str(self)

  # abstract classmethod
  @classmethod
  def default(cls) -> 'cls':
    "Create a default instance or raise TypeError"
    raise TypeError('default not defined')

  @classmethod
  def from_ints(cls,
      i: typing.Iterable[int],
      **kwgs
    ) -> 'cls':
    """
    Create an instance from the given iterable of integers of
    range 0--255.
    """
    # TODO: more docsting
    exp_num_bytes, exp_num_bits = divmod(cls._octets, 8)
    exp_len = exp_num_bytes + bool(exp_num_bits)
    iter_i = iter(i)
    ints = [next(iter_i) for _ in range(exp_len)]
    if len(ints) != exp_len:
      efs = 'expected number of integers was {}; got {}'
      raise ValueError(efs.format(exp_len, len(ints)))
    kwgs['_from'] = False
    return cls(ints, **kwgs)

  @classmethod
  def from_str(cls,
      s: typing.Iterable[str],
      *,
      ignored: str = ' _|',
      **kwgs
    ) -> 'cls':
    """
    Create an instance from an iterable that should yield
    character strings of hexdigit pairs.

    See si.utils.bconv.str2bytes()
    """
    exp_num_bytes, exp_num_bits = divmod(cls._octets, 8)
    exp_len = exp_num_bytes + bool(exp_num_bits)
    exp_len *= 2  # pairs of hexdigits per byte
    iter_s = iter(s)
    ints = [next(iter_s) for _ in range(exp_len)]
    if len(ints) != exp_len:
      efs = 'expected number of hexdigits was {}; got {}'
      raise ValueError(efs.format(exp_len, len(ints)))
    kwgs['_from'] = False
    return cls(_bconv.str2ints(ints, ignored=ignored), **kwgs)

  # abstract classmethod
  @classmethod
  def from_obj(cls, obj: typing.Any) -> 'cls':
    "Create an instance from the given object."
    raise NotImplementedError('must be defined by subclasses')

  @property
  def octets(self) -> int:
    "Size in bits"
    if self._octets == NotImplemented:
      efs = '{}: expected an explicit or None self._octets'
      raise NotImplementedError(efs.format(
          self.__class__.__name__))
    elif self._octets is None:
      return self._octets
    else:
      return self._octets

  def _check_octets(self) -> typing.Tuple[int, int, int]:
    """
    Check octets.

    Called by __init__ and should raise
    * RuntimeError if cls._octets was given wrong,
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
    exp_num_bytes, exp_num_bits = divmod(self.octets, 8)
    exp_num_bytes_ = exp_num_bytes + bool(exp_num_bits)
    if exp_num_bytes_ != num_bytes:
      efs = '{}: invalid length (expected {}): {}'
      raise ValueError(efs.format(self.__class__.__name__,
          exp_num_bytes_, num_bytes))
    return num_bytes, exp_num_bytes, exp_num_bits

  # abstract method
  @classmethod
  def obj(self) -> typing.Any:
    "Return the object the data represent."
    raise NotImplementedError('must be defined by subclasses')



################################################################
# BASE CLASSES                                                 #
################################################################


class Bytes(BaseBytes):
  BITWISE, BYTEWISE = False, True

  def __init__(self, *args, **kwgs):
    super().__init__()
    exp_num_bytes, exp_num_bits = divmod(self.octets, 8)
    if exp_num_bits:
      efs = ('{}: invalid cls._octets for Bytes: modulo 8 ',
          'should have been zero')
      raise RuntimeError(efs.format(self.__class__.__name__))
    if exp_num_bytes != len(self):
      efs = '{}: invalid length (expected {}): {}'
      raise ValueError(efs.format(self.__class__.__name__,
          exp_num_bytes, len(self)))

  def _check_octets(self) -> typing.Tuple[int, int, int]:
    "See BaseBytes._check_octets()"
    t_ = super()._check_octets()
    num_bytes, exp_num_bytes, exp_num_bits = t_
    if exp_num_bits:
      efs = ('{}: invalid cls._octets for Bytes: modulo 8 ',
          'should have been zero')
      raise RuntimeError(efs.format(self.__class__.__name__))
    return num_bytes, exp_num_bytes, exp_num_bits


class Bits(BaseBytes):
  BITWISE, BYTEWISE = True, False

  def __str__(self):
    return _bconv.bits2str(_bconv.ints2bits(self))

  @classmethod
  def from_bits(cls,
      b: typing.Iterable[int],
      **kwgs
    ) -> 'cls':
    """
    Create an instance from the given iterable of bits
    (integers of range 0--1).
    """
    exp_len = cls._octets
    iter_b = iter(b)
    bits = [next(iter_b) for _ in range(exp_len)]
    if len(bits) != exp_len:
      efs = 'expected number of bits was {}; got {}'
      raise ValueError(efs.format(exp_len, len(bits)))
    exp_num_bytes, exp_num_bits = divmod(exp_len, 8)
    num_pad_bits = 8 - exp_num_bits
    ints = _bconv.bits2ints([0] * num_pad_bits + bits)
    return cls.from_ints(ints)

  @classmethod
  def from_str(cls,
      s: typing.Iterable[str],
      *,
      bitchars: typing.Union[None, str] = None,
      ignored: str = ' _|',
    ) -> 'cls':
    """
    Create an instance from the given iterable that should
    yield character strings of bitdigits.

    See si.utils.bconv.str2bits()
    """
    b = _bconv.str2bits(s, bitchars=bitchars, ignored=ignored)
    return cls.from_bits(b)

  def _check_octets(self) -> typing.Tuple[int, int, int]:
    "See BaseBytes._check_octets()"
    t_ = super()._check_octets()
    num_bytes, exp_num_bytes, exp_num_bits = t_
    if self[0] & 2**8-2**exp_num_bits:
      efs = '{}: first value expected to be less than {}'
      raise ValueError(efs.format(self.__class__.__name__,
          2**exp_num_bits))
    return num_bytes, exp_num_bytes, exp_num_bits


class DictBytes(Bytes):
  # TODO: docstring
  _FROM_ORDER = ('items',)
  _octets = None
  _schema = _MappingProxyType({})

  @staticmethod
  def _bytes_from_items(items):
    if hasattr(items, 'values'):
      gen = items.values()
    else:
      gen = iter(items)
    bytes_, last_byte_val = b'', 0b0
    octets, last_byte_bits = 0o0, 0o0
    for item in gen:
      item_num_bytes, item_num_bits = divmod(item.octets, 8)
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

  @staticmethod
  def _schema_from_tuple(
      t: typing.Tuple[typing.Tuple[str, type]]
    ) -> _MappingProxyType:
    return _MappingProxyType(_collections.OrderedDict(t))

  def __new__(cls, *args,
      _check_octets: bool = True,
      _from: typing.Union[None, bool, str] = None,
      _from_exc: typing.Union[Exception, None] = None,
      _octets: typing.Union[None, int] = None,
      _items: typing.Union[None, _MappingProxyType] = None,
      **kwgs
    ) -> 'cls':
    inst = super().__new__(cls, *args,
        _check_octets = False,
        _from = _from,
        _from_exc = _from_exc,
        _octets = _octets,
        **kwgs)
    if _items:
      inst._items = _items
    elif not hasattr(inst, '_items'):
      inst._items = inst._get_items()
    if cls._octets is None and not hasattr(inst, '_octets'):
      inst._octets = inst._get_octets()
    elif _check_octets:
      inst._check_octets()
    return inst

  @classmethod
  def clskeys(cls) -> typing.Tuple[str]:
    """
    Return the keys of the representing object
    """
    return cls._schema.keys()

  @classmethod
  def default(cls) -> 'cls':
    """
    Create a default instance
    """
    return cls.from_items({item_name: item_cls.default()
        for (item_name, item_cls) in cls._schema.items()})

  @classmethod
  def from_items(cls,
      _dict: typing.Union[None, dict] = None,
      *,
      _from_obj: bool = False,
      _check_octets: bool = True,
      _octets: typing.Union[None, int] = None,
      **itms
    ) -> 'cls':
    "Create an instance from items" # TODO more docstring
    if _dict is None:
      unknw_k = set(itms.keys()) - set(cls._schema.keys())
      if unknw_k:
        efs = 'invalid key{}: {}'
        raise KeyError(efs.format(
            ('s' if len(unknw_k) > 1 else ''),
            ', '.join('{!r}'.format(k)
                for k in sorted(unknw_k))))
      _dict = itms
    else:
      if itms:
        raise TypeError('eiher a dictionary or items')
    _items = _collections.OrderedDict()
    for item_name, item_cls in cls._schema.items():
      item_obj = _dict.get(item_name)
      if _from_obj:
        item_inst = item_cls.from_obj(item_obj)
      elif item_obj is None:
        try:
          item_inst = item_cls.default()
        except AttributeError:
          efs = 'item must be defined explicitely: {}'
          raise TypeError(efs.format(item_name)) from None
      else:
        item_inst = item_cls(item_obj)
      _items[item_name] = item_inst
    arg = cls._bytes_from_items(_items)
    _items = _MappingProxyType(_items)
    return cls(arg, _from=False, _items=_items,
        _check_octets=_check_octets, _octets=_octets)

  @classmethod
  def from_obj(cls,
      _dict: typing.Union[None, dict] = None,
      **itms
    ) -> 'cls':
    "Create an instance from a dictionary" # TODO more docstring
    return cls.from_items(_dict, _from_obj=True, **itms)

  def __getitem__(self, item):
    if isinstance(item, str):
      return self.items[item]
    else:
      return super().__getitem__(item)

  @property
  def items(self):
    return self._items

  def _check_octets(self) -> typing.Tuple[int, int, int]:
    "See BaseBytes._check_octets()"
    t_ = super()._check_octets()
    if self.__class__._octets is not None:
      return t_
    else:
      num_bytes, exp_num_bytes, exp_num_bits = t_
      octets = 8 * exp_num_bytes + exp_num_bits
      exp_octets = self._get_octets()
      if octets != exp_octets:
        efs = '{}: invalid octets (expected {}): {}'
        raise ValueError(efs.format(self.__class__.__name__,
            exp_octets, octets))
      return num_bytes, exp_num_bytes, exp_num_bits

  def _get_items(self):
    _items = _collections.OrderedDict()
    bitwise = False
    o = 0
    for item_name, item_cls in self._schema.items():
      item_bitwise = item_cls.BITWISE
      if bitwise and not item_bitwise:
        aes = ('switching to bytewise: octets index must have '
            'no remainder after divided by 8')
        assert not o % 8, aes
      bitwise = item_bitwise
      o_num_bytes, o_num_bits = divmod(o, 8)
      gen = self[o_num_bytes:]
      if bitwise:
        clsmeth_name = 'from_bits'
        gen = _bconv.ints2bits(gen)
        # throw away
        for _ in range(o_num_bits):
          next(gen)
      else:
        clsmeth_name = 'from_ints'
      try:
        item_inst = getattr(item_cls, clsmeth_name)(gen)
      except StopIteration:
        efs = '{}: not enough {}'
        raise ValueError(efs.format(self.__class__.__name__,
            'bits' if bitwise else 'bytes'))
      _items[item_name] = item_inst
      o += item_inst.octets
    return _MappingProxyType(_items)

  def _get_octets(self):
    return sum((i.octets for i in self.items.values()))

  def obj(self):
    return _collections.OrderedDict((name, (item.obj()
        if hasattr(item, 'obj') else item))
        for name, item in self.items.items())



################################################################
# UTILITY CLASSES                                              #
################################################################


class PadBit(Bits):
  # TODO: docstring

  _octets = 0o1

  def __new__(cls, *args, **kwgs) -> 'cls':
    if not args:
      num_bytes, num_bits = divmod(cls._octets, 8)
      num_bytes += bool(num_bits)
      args = bytes(num_bytes),
      kwgs['_from'] = False
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


def PadBits(octets):
  # TODO: docstring
  return type('PadBits', (PadBit,), dict(_octets=octets))


del typing
