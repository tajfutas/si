#TODO: docstring

import collections as _collections
from types import MappingProxyType as _MappingProxyType
import typing

from .. import base
from .. import bconv as _bconv
from .. import factorymethod


class NamedTupleBytesMeta(type):

  def __new__(cls, typename, bases, ns):
    if ns.get('_root', False) or ns.get('_untampered', False):
      return super().__new__(cls, typename, bases, ns)
    t = [(n, c) for n, c in ns.items() if not n.startswith('_')]
    for n, c in t:
      del ns[n]
    name = f'{typename}Tuple'
    tpl = _collections.namedtuple(name, (n for n, c in t))
    ns['_tpl'] = tpl
    schema = tpl(*(c for n, c in t))
    ns['_schema'] = schema
    return super().__new__(cls, typename, bases, ns)

  @property
  def schema(cls):
    "NamedTuple of Data Schema"
    return cls._schema

  @property
  def tpl(cls):
    "NamedTuple class of the underlying object."
    return cls._tpl


class NamedTupleBytes(base.BytesBase,
    metaclass=NamedTupleBytesMeta):
  # TODO: docstring
  _root = True
  _bitsize = None
  _schema = _MappingProxyType({})

  @staticmethod
  def _get_bytes(fields):
    bytes_, last_byte_val = b'', 0b0
    bitsize, last_byte_bits = 0o0, 0o0
    for field in fields:
      field_num_bytes, field_num_bits = divmod(field.bitsize, 8)
      if field_num_bytes:
        if last_byte_val:
          efs = 'received bytes in bitwise mode: {!r}'
          raise ValueError(efs.format(field))
        else:
          bytes_ += field[:field_num_bytes]
          bitsize += 8 * field_num_bytes
      if field_num_bits:
        Lb, Ib = last_byte_bits, field_num_bits
        S = shift = Lb + Ib - 8
        B = field[-1] & 2**Ib-2**max(0, S)
        if 0 <= S:
          B >>= S
          bytes_ += bytes((last_byte_val + B,))
          bitsize += 0o10
          last_byte_val = field[-1] & 2**S-1
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
  def _get_schema(
      t: typing.Tuple[typing.Tuple[str, type]]
    ) -> _MappingProxyType:
    return _MappingProxyType(_collections.OrderedDict(t))

  def __new__(cls, *args,
      check_bitsize: bool = True,
      factory_meth: typing.Union[None, bool, str] = None,
      _fields: typing.Union[None, tuple] = None, # TODO
      **kwgs
    ) -> 'cls':
    inst = super().__new__(cls, *args,
        check_bitsize = False,
        factory_meth = factory_meth,
        **kwgs)
    if _fields:
      inst._fields = _fields
    elif not hasattr(inst, '_fields'):
      inst._fields = inst._get_fields()
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
  @factorymethod.default
  def default(cls, *,
      check_bitsize:bool=False, **kwgs
    ) -> 'cls':
    """
    Create a default instance
    """
    return cls.from_obj(cls.tpl(*(field.default()
      for field in cls.schema)))

  @classmethod
  def from_obj(cls,
      arg: typing.Union[None, tuple] = None,
      *,
      check_bitsize: bool = True,
      from_obj: bool = False,
      **fields
    ) -> 'cls':
    "Create an instance from ..." # TODO more docstring
    if arg is None:
      unknw_flds = set(fields.keys()) - set(cls.schema._fields)
      if unknw_flds:
        efs = 'invalid key{}: {}'
        raise KeyError(efs.format(
            ('s' if len(unknw_flds) > 1 else ''),
            ', '.join('{!r}'.format(k)
                for k in sorted(unknw_flds))))
      arg = fields
    else:
      if fields:
        raise TypeError('eiher a tuple or field keywords')
    schema = cls.schema  # μ-o
    _fields = [None] * len(schema)
              # known size: faster to set than append to empty
    fielditems = zip(schema._fields, schema)
    for i, (field_name, field_cls) in enumerate(fielditems):
      field_obj = arg.get(field_name)
      if from_obj:
        field_inst = field_cls.from_obj(field_obj)
      elif field_obj is None:
        try:
          field_inst = field_cls.default()
        except AttributeError:
          efs = 'field must be defined explicitely: {}'
          raise TypeError(efs.format(field_name)) from None
      else:
        field_inst = field_cls(field_obj)
      _fields[i] = field_inst
    arg = cls._get_bytes(_fields)
    _fields = cls.tpl(*_fields)
    return cls(arg, check_bitsize=check_bitsize,
      factory_meth=False, _fields=_fields)

  def __getitem__(self, item):
    if isinstance(item, str):
      return self.items[item]
    else:
      return super().__getitem__(item)

  @property
  def fields(self):
    return self._fields

  @property
  def schema(self):
    "NamedTuple of Data Schema"
    return self.__class__._schema

  @property
  def tpl(self):
    "NamedTuple class of the underlying object."
    return self.__class__._tpl

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

  def _get_fields(self):
    schema = self.schema  # μ-o
    _fields = [None] * len(schema)
              # known size: faster to set than append to empty
    fielditems = zip(schema._fields, schema)
    bitwise = False
    o = 0
    for i, (field_name, field_cls) in enumerate(fielditems):
      field_bitwise = field_cls.BITWISE
      if bitwise and not field_bitwise:
        aes = ('switching to bytewise: bitsize index must have '
            'no remainder after divided by 8')
        assert not o % 8, aes
      bitwise = field_bitwise
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
        field_inst = getattr(field_cls, clsmeth_name)(gen)
      except StopIteration:
        efs = '{}: not enough {}'
        raise ValueError(efs.format(self.__class__.__name__,
            'bits' if bitwise else 'bytes'))
      _fields[i] = field_inst
      o += field_inst.bitsize
    return self.tpl(*_fields)

  def _get_bitsize(self):
    return sum(f.bitsize for f in self.fields)

  def obj(self):
    return self.__class__.tpl(*(field.obj()
        for field in self.fields))


del typing

del base
del factorymethod
