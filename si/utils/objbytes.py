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

For more information about instantiation, see help page of
BaseBytes class.
"""

import collections as _collections
import io as _io
from types import MappingProxyType as _MappingProxyType
import typing

from . import bconv as _bconv
from .methdeco import eliminate_first_arg_if_none, \
    none_if_first_arg_is_none



################################################################
# FACTORY METHOD DECORATORS                                    #
################################################################


default = eliminate_first_arg_if_none
default_if_arg_is_none = none_if_first_arg_is_none



################################################################
# SUPERCLASS                                                   #
################################################################


class BaseBytes(bytes):
  """
  Superclass of all objbytes classes. Subclass of bytes.
  Every objbytes class should be inherited by this class.

  Subclasses must define the following
  * class constant:
    - _bitsize: integer or None
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

  If variable size then must define also the following
  * classmethod:
    - from_ints()
    - from_str()

  See the above methods' help page for more information about
  their purpose.

  Subclasses may optionally definde the following
  * classmethod:
    - default()
      Return the default instance. Recommended to be defined if
      such an object exist.

  By default objbytes instances can be made by passing either
  the underlying object (serialization) or its databytes
  (deserialization is then done with obj() method).

  Fro more info about this see help of __new__.

  they should represent or a bytes-like object (which
  is checked for having a decode method) containing the data.
  In addition, there are other special ways of instantiating and
  each of them is represented by a from_something() classmethod.

  If the subclass has a default value, then it can be
  instantiated by passing no arguments to the class.
  """

  _SERA_FMETH_ORDER = ('from_obj', 'default')
                      # type: typing.Tuple[str]
  """
  During serialization attempt (see help of __new__), this tuple
  is looped over for factory method names whose corresponding
  factory method is then attempted to provide an instance
  without errors.

   Defines the fallback order of factory methods which are
  attempted to return an instance for the given arguments
  by __new__() before finally falling back to the superclass'
  (bytes) __new__(),  . If the factory method
  return None that triggers a fallback. ValueError and TypeError
  exceptions are also causing a fallback. If however __new__ was
  called with a factory_meth = True attribute then these
  exceptions are raised before the final fallback.
  """

  _bitsize = NotImplemented  # type: typing.Union[None, int]
  """
  Size of the serialized data in bits or None if variable size.
  Must be overridden by subclasses.
  """

  def __new__(cls, *args,
      check_bitsize: bool = True,
      bitsize: typing.Union[None, int] = None,
      factory_meth: typing.Union[None, bool, str,
          typing.Callable[...,'cls']] = None,
      **kwgs
    ) -> 'cls':
    """
    Create a new instance.

    Accepts at most a single positional argument, and that must
    be the underlying object (serialization) or its databytes
    (deserialization is then done with obj() method).

    Serialization attempt is done if factory_meth keyword
    argument is None (default) and argument is not a bytes-like
    object (checked for having a 'decode' method), or if
    factory_meth is True.

    During serialization attempt, _SERA_FMETH_ORDER tuple is
    looped over for factory method names whose corresponding
    factory method is then attempted to provide an instance
    without errors. If none of them is capable to do that and
    if factory_meth is None then as a final fallback, argument
    is passed finally to the superclass' (bytes) __new__().
    If a factory method return None then next one comes. Same
    applies to raised ValueError and TypeError exceptions. If
    however factory_meth is True then the last exception of
    those gets raised and no final fallback is made.

    Explicit serialization is done (the corresponding factory
    method is called) if factory_meth is callable or is the name
    of a factory method defined in the class.

    No serialization is done if factory_meth keyword argument is
    False.

    Important! All factory methods must explicitely set
    factory_meth = False in their return cls(...) line or
    decorated with @factory_method.

    If the underlying object is serialized to variable size bits
    (set objbytes subclass' _bitsize = None) and the expected
    bitsize can be less than 8 * bytesize then factory methods
    must explicitely set bitsize value with the bitsize keyword
    argument. Note that this must be a rare case.

    By default, instances are checked/validated for their size
    which can be turned off with check_bitsize = False keyword
    argument, especially to speed up instantiation of tested
    code.
    """
    # TODO: @factory_method
    inst = None
    if 1 < len(args):
      efs = ('{}() takes at most 1 positional argument but {} '
          'were given')
      raise TypeError(efs.format(cls.__name__, len(args)))
    arg = args[0] if args else None
    factory_meth_exc = None
    if factory_meth is None and hasattr(arg, 'decode'):
      pass  # is bytes-like, delegated to super().__new__()
    elif factory_meth is None or factory_meth is True:
      for method_name in cls._SERA_FMETH_ORDER:
        try:
          inst = getattr(cls, method_name)(arg,
              check_bitsize=check_bitsize, **kwgs)
        except (ValueError, TypeError) as e:
          factory_meth_exc = e
        else:
          if inst is not None:
            factory_meth_exc = None
            break
      else:
        if factory_meth is True and factory_meth_exc:
          raise factory_meth_exc
    elif factory_meth:
      if hasattr(factory_meth, '__call__'):
        fmethod = factory_meth
      else:
        fmethod = getattr(cls, factory_meth)
      inst = fmethod(*args, check_bitsize=check_bitsize, **kwgs)
    if inst is None:
      inst = super().__new__(cls, *args, **kwgs)
    has_cls_bitsize = cls._bitsize is None  # μ-o
    if bitsize:
      if not has_cls_bitsize:
        efs = ('{}: attempt to set instance bitsize for a '
            'fixed size data')
        raise ValueError(efs.format(cls.__name__))
      inst._bitsize = bitsize
    elif has_cls_bitsize:
      inst._bitsize = 8 * len(inst)
    if check_bitsize:
      inst._check_bitsize()
    return inst

  def __repr__(self):
    return '{}({})'.format(self.__class__.__name__,
        super().__repr__())

  def __str__(self):
    return _bconv.ints2str(self)

  # abstract classmethod
  @classmethod
  @default
  def default(cls,
      check_bitsize: bool = False,  # should be overridden
    ) -> 'cls':
    "Create a default instance or raise TypeError"
    raise TypeError('default not defined')

  @classmethod
  def from_ints(cls,
      i: typing.Iterable[int],
      **kwgs
    ) -> 'cls':
    """
    Create an instance from the given iterable of integers of
    range 0--255. Each integer represent a byte in this aspect.

    Note that bytes and bytearray objects are also iterables of
    such integers.

    Consumes only the required number of integers from the given
    iterable which determines the data. Note that this may be
    more than the actual content of the data (i.e. when end of
    an array is indicated by a specific value).
    """
    exp_num_bytes, exp_num_bits = divmod(cls._bitsize, 8)
    exp_len = exp_num_bytes + bool(exp_num_bits)
    iter_i = iter(i)
    ints = [next(iter_i) for _ in range(exp_len)]
    if len(ints) != exp_len:
      efs = 'expected number of integers was {}; got {}'
      raise ValueError(efs.format(exp_len, len(ints)))
    kwgs['factory_meth'] = False
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

    For more info, see help page of si.utils.bconv.str2bytes().

    Consumes only the required number of characters from the
    given iterable which determines the data. Note that this may
    be more than the actual content of the data (i.e. when end
    of an array is indicated by a specific value).
    """
    exp_num_bytes, exp_num_bits = divmod(cls._bitsize, 8)
    exp_len = exp_num_bytes + bool(exp_num_bits)
    exp_len *= 2  # pairs of hexdigits per byte
    iter_s = iter(s)
    ints = [next(iter_s) for _ in range(exp_len)]
    if len(ints) != exp_len:
      efs = 'expected number of hexdigits was {}; got {}'
      raise ValueError(efs.format(exp_len, len(ints)))
    kwgs['factory_meth'] = False
    return cls(_bconv.str2ints(ints, ignored=ignored), **kwgs)

  # abstract classmethod
  @classmethod
  @default_if_arg_is_none
  def from_obj(cls, obj: typing.Any, **kwgs) -> 'cls':
    "Create an instance from the given object."
    raise NotImplementedError('must be defined by subclasses')

  @property
  def bitsize(self) -> int:
    "Size in bits"
    if self._bitsize == NotImplemented:
      efs = '{}: expected an explicit or None self._bitsize'
      raise NotImplementedError(efs.format(
          self.__class__.__name__))
    else:
      return self._bitsize

  def _check_bitsize(self) -> typing.Tuple[int, int, int]:
    """
    Check bitsize.

    Called by __init__ and should raise
    * RuntimeError if cls._bitsize was given wrong,
    * ValueError if the size by the given value would be wrong.

    Return (num_bytes, exp_num_bytes, exp_num_bits) tuple, which
    is a micro-optimization for subclasses which should define
    their _check_bitsize() with the following first two lines:
      t_ = super()._check_bitsize()
      num_bytes, exp_num_bytes, exp_num_bits = t_
    Similarly, _check_bitsize() in subclasses should return:
      return num_bytes, exp_num_bytes, exp_num_bits
    """
    num_bytes = len(self)
    exp_num_bytes, exp_num_bits = divmod(self.bitsize, 8)
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
  """
  Base class of all objbytes objects which are represented by
  bytes and not bits.

  Its bitsize must be divisible by 8 without remainder and that
  is checked during instatntiation.
  """
  BITWISE, BYTEWISE = False, True

  def __new__(cls, *args,
      check_bitsize: bool = True,
      factory_meth: typing.Union[None, bool, str,
          typing.Callable[...,'cls']] = None,
      **kwgs
    ) -> 'cls':
    # TODO: docstring
    return super().__new__(cls, *args,
        check_bitsize = check_bitsize,
        factory_meth = factory_meth,
        **kwgs)

  def _check_bitsize(self) -> typing.Tuple[int, int, int]:
    """
    Validate datasize.

    For more info, see BaseBytes._check_bitsize()
    """
    t_ = super()._check_bitsize()
    num_bytes, exp_num_bytes, exp_num_bits = t_
    if exp_num_bits:
      efs = ('{}: invalid cls._bitsize for Bytes: it must ',
          'be divisible by 8 without remainder')
      raise RuntimeError(efs.format(self.__class__.__name__))
    if exp_num_bytes != len(self):
      efs = '{}: invalid length (expected {}): {}'
      raise ValueError(efs.format(self.__class__.__name__,
          exp_num_bytes, len(self)))
    return num_bytes, exp_num_bytes, exp_num_bits


class Bits(BaseBytes):
  """
  Base class of all objbytes objects which are represented by
  bits and not bytes.
  """
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
    exp_len = cls._bitsize
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

  def _check_bitsize(self) -> typing.Tuple[int, int, int]:
    "See BaseBytes._check_bitsize()"
    t_ = super()._check_bitsize()
    num_bytes, exp_num_bytes, exp_num_bits = t_
    if self[0] & 2**8-2**exp_num_bits:
      efs = '{}: first value expected to be less than {}'
      raise ValueError(efs.format(self.__class__.__name__,
          2**exp_num_bits))
    return num_bytes, exp_num_bytes, exp_num_bits


class DictBytes(Bytes):
  # TODO: docstring
  _SERA_FMETH_ORDER = ('from_items', 'default')
  _bitsize = None
  _schema = _MappingProxyType({})

  @staticmethod
  def _bytesfactory_meth_items(items):
    if hasattr(items, 'values'):
      gen = items.values()
    else:
      gen = iter(items)
    bytes_, last_byte_val = b'', 0b0
    bitsize, last_byte_bits = 0o0, 0o0
    for item in gen:
      item_num_bytes, item_num_bits = divmod(item.bitsize, 8)
      if item_num_bytes:
        if last_byte_val:
          efs = 'received bytes in bitwise mode: {!r}'
          raise ValueError(efs.format(item))
        else:
          bytes_ += item[:item_num_bytes]
          bitsize += 8 * item_num_bytes
      if item_num_bits:
        Lb, Ib = last_byte_bits, item_num_bits
        S = shift = Lb + Ib - 8
        B = item[-1] & 2**Ib-2**max(0, S)
        if 0 <= S:
          B >>= S
          bytes_ += bytes((last_byte_val + B,))
          bitsize += 0o10
          last_byte_val = item[-1] & 2**S-1
          last_byte_val <<= 8-S
          last_byte_bits = S
        else:
          B <<= -S
          last_byte_val += B
          last_byte_bits += Ib
          bitsize += Ib
    else:
      if last_byte_val:
        raise ValueError('finished in bitwise mode')
    return bytes_

  @staticmethod
  def _schemafactory_meth_tuple(
      t: typing.Tuple[typing.Tuple[str, type]]
    ) -> _MappingProxyType:
    return _MappingProxyType(_collections.OrderedDict(t))

  def __new__(cls, *args,
      check_bitsize: bool = True,
      factory_meth: typing.Union[None, bool, str] = None,
      _items: typing.Union[None, _MappingProxyType] = None,
      **kwgs
    ) -> 'cls':
    inst = super().__new__(cls, *args,
        check_bitsize = False,
        factory_meth = factory_meth,
        **kwgs)
    if _items:
      inst._items = _items
    elif not hasattr(inst, '_items'):
      inst._items = inst._get_items()
    elif check_bitsize:
      inst._check_bitsize()
    return inst

  @classmethod
  def clskeys(cls) -> typing.Tuple[str]:
    """
    Return the keys of the representing object
    """
    return cls._schema.keys()

  @classmethod
  @default
  def default(cls, *,
      check_bitsize:bool=False, **kwgs
    ) -> 'cls':
    """
    Create a default instance
    """
    return cls.from_items({item_name: item_cls.default()
        for (item_name, item_cls) in cls._schema.items()})

  @classmethod
  @default_if_arg_is_none
  def from_items(cls,
      _dict: typing.Union[None, dict] = None,
      *,
      check_bitsize: bool = True,
      from_obj: bool = False,
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
      if from_obj:
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
    arg = cls._bytesfactory_meth_items(_items)
    _items = _MappingProxyType(_items)
    return cls(arg, check_bitsize=check_bitsize,
      factory_meth=False, _items=_items)

  @classmethod
  @default_if_arg_is_none
  def from_obj(cls,
      _dict: typing.Union[None, dict] = None,
      **itms
    ) -> 'cls':
    "Create an instance from a dictionary" # TODO more docstring
    return cls.from_items(_dict, from_obj=True, **itms)

  def __getitem__(self, item):
    if isinstance(item, str):
      return self.items[item]
    else:
      return super().__getitem__(item)

  @property
  def items(self):
    return self._items

  def _check_bitsize(self) -> typing.Tuple[int, int, int]:
    "See BaseBytes._check_bitsize()"
    t_ = super()._check_bitsize()
    if self.__class__._bitsize is not None:
      return t_
    else:
      num_bytes, exp_num_bytes, exp_num_bits = t_
      bitsize = 8 * exp_num_bytes + exp_num_bits
      exp_bitsize = self._get_bitsize()
      if bitsize != exp_bitsize:
        efs = '{}: invalid bitsize (expected {}): {}'
        raise ValueError(efs.format(self.__class__.__name__,
            exp_bitsize, bitsize))
      return num_bytes, exp_num_bytes, exp_num_bits

  def _get_items(self):
    _items = _collections.OrderedDict()
    bitwise = False
    o = 0
    for item_name, item_cls in self._schema.items():
      item_bitwise = item_cls.BITWISE
      if bitwise and not item_bitwise:
        aes = ('switching to bytewise: bitsize index must have '
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
      o += item_inst.bitsize
    return _MappingProxyType(_items)

  def _get_bitsize(self):
    return sum((i.bitsize for i in self.items.values()))

  def obj(self):
    return _collections.OrderedDict((name, (item.obj()
        if hasattr(item, 'obj') else item))
        for name, item in self.items.items())



################################################################
# UTILITY CLASSES                                              #
################################################################


class PadBit(Bits):
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
  return type('PadBits', (PadBit,), dict(_bitsize=bitsize))


del typing

del eliminate_first_arg_if_none
del none_if_first_arg_is_none
