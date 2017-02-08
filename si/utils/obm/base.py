import copy as _copy

from . import singleton as _s


class Field:

  def __init__(self, *args, set_different_only=True, **kwgs):
    self.set_different_only = set_different_only
    pass

  def __get__(self, instance, owner=None):
    if instance is None:
      return self
    else:
      return instance._fields[self.name].obj

  def __set__(self, instance, value):
    field = instance._fields[self.name]
    if self.set_different_only:
      old_value = self.__get__(instance)
      if old_value == value:
        return
    else:
      old_value = _s.Unknown
    field.obj = value
    instance._on_updated(self.name, value, old_value)


  def __set_name__(self, owner, name):
    self.name = name


class BaseMeta(type):

  def __new__(cls, typename, bases, ns):
    fields = ns.get('__annotations__', {})
    klass = super().__new__(cls, typename, bases, ns)
    for name, fieldobj in fields.items():
      field = fieldobj._field_class()
      field.__set_name__(klass, name)
      setattr(klass, name, field)
    return klass


class Base(metaclass=BaseMeta):

  _parent = None
  _bitsize = None
  _field_class = Field

  def __init__(self, *args, default=_s.NotSet, readonly=False,
      **kwgs):
    self._bit_index = _s.NotSet
    self._default = default
    self._readonly = readonly
    self._setup = 0b00
    self._obj = _s.NotSet
    self._dat = _s.NotSet
    self._fields = {}
    self._children_notset = set()
    fields = getattr(self, '__annotations__', {})
    if fields:
      i = 0
      for name, fieldobj in fields.items():
        has_bitsize = self._bitsize not in (None, ...)
        fieldobj = _copy.deepcopy(fieldobj)
        fieldobj._bit_index = i
        fieldobj._parent = self
        if fieldobj._obj is _s.NotSet:
          self._children_notset.add(name)
        self._fields[name] = fieldobj
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
      if not self._children_notset:
        self._assemble_dat()
    else:
      if default != _s.NotSet:
        self.obj = default

  @classmethod
  def _get_field(cls, *args, **kwgs):
    return Field(*args, **kwgs)

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
      if self._fields:
        pass # TODO
      else:
        self._decode()
      self._setup |= 0b10
  @dat.deleter
  def dat(self):
    if self._default != _s.NotSet:
      self.obj = self._default
    else:
      raise NotImplementedError()

  @property
  def obj(self):
      if self._fields:
        return tuple(fieldobj.obj
            for fieldobj in self._fields.values())
      else:
        return self._obj
  @obj.setter
  def obj(self, new_obj):
    if self._fields:
      assert len(new_obj) == len(self._fields)
      it = enumerate(self._fields.items())
      indices = []
      for i, (name, fieldobj) in it:
        if new_obj[i] != fieldobj.obj:
          self._children_notset.add(name)
          indices.append((i, fieldobj))
      for i, fieldobj in indices:
        fieldobj.obj = new_obj[i]
    else:
      old_obj = self._obj
      if self._setup and self._readonly:
        raise AttributeError('can\'t set attribute')
      do = self.validate_obj(new_obj)
      if do:
        self._obj = new_obj
        if self._fields:
          pass # TODO
        else:
          self._encode()
        self._setup |= 0b01
  @obj.deleter
  def obj(self):
    if self._default != _s.NotSet:
      self.obj = self._default
    else:
      raise NotImplementedError()

  @property
  def parent(self):
      return self._parent

  @property
  def setup(self):
      return self._setup

  def _decode(self):
    raise NotImplementedError()

  def _encode(self):
    raise NotImplementedError()

  def _assemble_dat(self):
    dat = bytearray()
    for name, fieldobj in self._fields.items():
      if not fieldobj._bit_index % 8:
        dat.extend(fieldobj.dat)
    self.dat = dat
    # visszaírom memoryviewkkal


  def _on_updated(self, name, new_value, old_value=_s.Unknown):
    children_notset = bool(self._children_notset)
    if children_notset:
      self._children_notset.remove(name)
      if children_notset and not self._children_notset:
        self._assemble_dat()

  def validate_dat(self, dat):
    return True

  def validate_obj(self, obj):
    return True
