import copy
import sys
import struct


class DescriptorBase:

  def __init__(self, *args, **kwgs):
    super().__init__(*args, **kwgs)

  def __get__(self, instance, owner):
    if instance is None:
      return self
    else:
      return instance._types[self.name].obj

  def __set__(self, instance, value):
    instance._types[self.name].obj = value

  # this is the new initializer:
  def __set_name__(self, owner, name):
    self.name = name

class IntegerField(DescriptorBase):
  pass


class BaseMeta(type):

  def __new__(cls, typename, bases, ns):
    if ns.get('_root', False):
      return super().__new__(cls, typename, bases, ns)
    types = ns.get('__annotations__', {})
    klass = super().__new__(cls, typename, bases, ns)
    for name, fieldobj in types.items():
      field = fieldobj._descriptor_class()
      field.__set_name__(klass, name)
      setattr(klass, name, field)
    return klass


class NotSet: pass

class Base(metaclass=BaseMeta):

  _root = True
  _bitsize = None
  _descriptor_class = DescriptorBase

  def __init__(self, *args, default=NotSet, readonly=False,
      **kwgs):
    self._bit_index = NotSet
    self._default = default
    self._readonly = readonly
    self._setup = 0b00
    self._obj = NotSet
    self._dat = NotSet
    self._types = {}
    types = getattr(self, '__annotations__', {})
    i = 0
    for name, fieldobj in types.items():
      has_bitsize = self._bitsize not in (None, ...)
      fieldobj = copy.deepcopy(fieldobj)
      fieldobj._bit_index = i
      fieldobj._parent = self
      self._types[name] = fieldobj
      if fieldobj.bitsize == ...:
        self._bitsize = ...
        i = ...
      else:
        if self._bitsize is None:
          self._bitsize = 0
        if self._bitsize != ...:
          self._bitsize += fieldobj._bitsize
        if i != ...:
          i += fieldobj.bitsize
    if default != NotSet:
      self.obj = default

  @property
  def bitsize(self):
      return self._bitsize

  @property
  def dat(self):
      return self._dat
  @dat.setter
  def dat(self, new_dat):
    old_dat = self._dat
    if self._setup and self._readonly:
      raise AttributeError('can\'t set attribute')
    do = self.validate_dat(new_dat)
    if do:
      self._dat = new_dat
      self._decode()
      self._setup |= 0b10
  @dat.deleter
  def dat(self):
    if self._default != NotSet:
      self.obj = self._default
    else:
      raise NotImplementedError()

  @property
  def obj(self):
      return self._obj
  @obj.setter
  def obj(self, new_obj):
    old_obj = self._obj
    if self._setup and self._readonly:
      raise AttributeError('can\'t set attribute')
    do = self.validate_obj(new_obj)
    if do:
      self._obj = new_obj
      self._encode()
      self._setup |= 0b01
  @obj.deleter
  def obj(self):
    if self._default != NotSet:
      self.obj = self._default
    else:
      raise NotImplementedError()

  @property
  def setup(self):
      return self._setup

  def _decode(self):
    raise NotImplementedError()

  def _encode(self):
    raise NotImplementedError()

  def validate_dat(self, dat):
    return True

  def validate_obj(self, obj):
    return True


class Integer(Base):


  _descriptor_class = IntegerField

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
      self._byteorder = sys.byteorder
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
      dat = struct.pack(self._typecode, self._obj)
    else:
      raise NotImplementedError()
    obj = struct.unpack(self._typecode, self._dat)[0]
    self._obj = obj
    self._setup |= 0b01

  def _encode(self):
    if self._typecode:
      dat = struct.pack(self._typecode, self._obj)
    else:
      raise NotImplementedError()
    if self._setup & 0b10:
      self._dat[:] = dat
    else:
      if not self._readonly:
        dat = bytearray(dat)
      self._dat = dat
      self._setup |= 0b10

class Test(Base):
  c : Integer(0o20, default=10)
  a : Integer(0o40, True, readonly=True)

x = Integer(0o10, True)

t = Test()
