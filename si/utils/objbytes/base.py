#TODO: docstring

import typing

from . import bconv as _bconv
from . import factorymethod



class ObjBytesMeta(type):

  @property  # classproperty
  def default_mode(cls):
    "False if the default mode is bytewise, True if bitwise."
    try:
      return sorted(cls._modes, reverse=True)[0]
    except IndexError:
      msg = 'no mode is allowed for the class'
      raise RuntimeError(msg) from None


class ObjBytes(bytes, metaclass=ObjBytesMeta):
  """
  Baseclass of all objbytes classes. Subclass of bytes.
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

  _sera_fmeth_order = ('from_obj', 'default')
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

  _modes = frozenset((1, 8))
  # TODO: docstring

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

    During serialization attempt, _sera_fmeth_order tuple is
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
    clsname = cls.__name__
    inst = None
    if 1 < len(args):
      raise TypeError((f'{clsname}() takes at most 1 '
          f'positional argument but {len(args)} were given'))
    arg = args[0] if args else None
    factory_meth_exc = None
    if factory_meth is None and hasattr(arg, 'decode'):
      pass  # is bytes-like, delegated to super().__new__()
    elif factory_meth is None or factory_meth is True:
      for method_name in cls._sera_fmeth_order:
        try:
          inst = getattr(cls, method_name)(arg,
              check_bitsize=check_bitsize, **kwgs)
        except (ValueError, TypeError) as e:
          factory_meth_exc = e
          raise
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
        raise ValueError((f'{clsname}: attempt to set instance '
            'bitsize for a fixed size data'))
      inst._bitsize = bitsize
    elif has_cls_bitsize:
      inst._bitsize = 8 * len(inst)
    del inst.mode  # sets mode to class default
    if check_bitsize:
      inst._check_bitsize()
    return inst

  def __repr__(self):
    return '{}({})'.format(self.__class__.__name__,
        super().__repr__())

  def __str__(self):
    mode = self.mode  # μ-o
    if mode == 8:
      return _bconv.ints2str(self)
    elif mode == 1:
      return _bconv.bits2str(_bconv.ints2bits(self))
    else:
      raise RuntimeError(f'unexpected mode: {mode}')

  # abstract classmethod
  @classmethod
  @factorymethod.default
  def default(cls,
      check_bitsize: bool = False,  # should be overridden
    ) -> 'cls':
    "Create a default instance or raise TypeError"
    raise TypeError('default not defined')

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
      mode: typing.Union[None, int] = None,
      **kwgs
    ) -> 'cls':
    """
    Create an instance from an iterable that should yield
    character strings.

    The behavior is determinde by the mode parameter which
    defaults to cls.default_mode if not set explicitely.

    If mode == 8 (bytewise) then the iterable should yield
    hexdigit pairs. For more info, see help page of
    bconv.str2ints().

    If mode == 1 (bitwise) then the iterable should yield
    bitdigits. For more info, see help page of bconv.str2bits().

    Consumes only the required number of characters from the
    given iterable which determines the data. Note that this may
    be more than the actual content of the data (i.e. when end
    of an array is indicated by a specific value).
    """
    if mode is None:
      mode = cls.default_mode
    if mode == 8:
      i = _bconv.str2ints(s, ignored=ignored)
      return cls.from_ints(i)
    elif mode == 1:
      b = _bconv.str2bits(s, bitchars=bitchars, ignored=ignored)
      return cls.from_bits(b)
    else:
      msg = 'invalid mode: 8 (bytewise) or 1 (bitwise) expected'
      raise ValueError(msg)


  # abstract classmethod
  @classmethod
  @factorymethod.default_if_arg_is_none
  def from_obj(cls, obj: typing.Any, **kwgs) -> 'cls':
    "Create an instance from the given object."
    raise NotImplementedError('must be defined by subclasses')

  @classmethod
  def new_subtype(cls,
      name: str,
      untampered: bool = True,
      **nskw) -> type:
    # TODO: docstring
    nskw['_untampered'] = bool(untampered)
    return cls.__class__(name, (cls,), nskw)

  @property
  def bitsize(self) -> int:
    "Size in bits"
    if self._bitsize == NotImplemented:
      efs = '{}: expected an explicit or None self._bitsize'
      raise NotImplementedError(efs.format(
          self.__class__.__name__))
    else:
      return self._bitsize

  @property
  def mode(self) -> bool:
    return self._mode
  @mode.setter
  def mode(self, value: int):
    if value in self._modes:
      self._mode = value
    else:
      msg = 'mode not allowed (allowed modes: {})'
      modes = sorted(str(m) for m in self._modes)
      raise ValueError(msg.format(', '.join(modes)))
  @mode.deleter
  def mode(self):
    self._mode = self.__class__.default_mode

  @property
  def modes(self) -> bool:
    return self._modes

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
    clsname = self.__class__.__name__
    if exp_num_bytes_ != num_bytes:
      raise ValueError((f'{clsname}: invalid length '
          f'(expected {exp_num_bytes_}): {num_bytes}'))
    mode = self.mode  # μ-o
    if mode == 8:
      if exp_num_bits:
        raise RuntimeError((f'{clsname}: invalid cls._bitsize '
            'in bytwise mode: it must be divisible with 8 '
            'without remainder'))
    elif mode == 1:
      if self[0] & 2**8-2**exp_num_bits:
        raise ValueError((f'{clsname}: first value expected '
            f'to be less than {2**exp_num_bits}'))
    else:
      raise RuntimeError(f'unexpected mode: {mode}')
    return num_bytes, exp_num_bytes, exp_num_bits  # μ-o

  # abstract method
  @classmethod
  def obj(self) -> typing.Any:
    "Return the object the data represent."
    raise NotImplementedError('must be defined by subclasses')


class Bytes(ObjBytes):
  """
  Base class of all objbytes objects which are represented by
  bytes and not bits.

  Its bitsize must be divisible by 8 without remainder and that
  is checked during instatntiation.
  """
  # TODO: docstring
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


class Bits(ObjBytes):
  """
  Base class of all objbytes objects which are represented by
  bits and not bytes.
  """
  # TODO: docstring
  BITWISE, BYTEWISE = True, False

  def __new__(cls, *args, **kwgs) -> 'cls':
    # TODO: docstring
    return super().__new__(cls, *args, **kwgs)


del typing
