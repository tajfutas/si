import sys

class BaseMeta(type):

  def __new__(cls, typename, bases, ns):
    print([cls, typename, bases])
    print(ns)
    if ns.get('_root', False):
      return super().__new__(cls, typename, bases, ns)
    types = ns.get('__annotations__', {})

    #print(types)
    klass = super().__new__(cls, typename, bases, ns)
    for name, fieldobj in types.items():
      field = fieldobj._get_field_()
      field.__set_name__(klass, name)
      setattr(klass, name, field)

    return klass
    return _make_nmtuple(typename, types.items())


class Base(metaclass=BaseMeta):

  def __init__(self, readonly=False):
    self._readonly = readonly
    types = getattr(self, '__annotations__', {})
    for name, fieldobj in types.items():
      fieldobj._set_parent_(self)

  @property
  def parent(self):
      return self._parent

  def _get_field_(self):
    return IntegerField(self)

  def _set_parent_(self, instance):
    self._parent = instance


class IntegerField:

  def __init__(self, fieldobj, *args, **kwgs):
    self.fieldobj = fieldobj
    super().__init__(*args, **kwgs)

  def __get__(self, instance, owner):
    if instance is None:
      return self
    else:
      return instance.__dict__[self.name]

  def __set__(self, instance, value):
    print('set', self, instance, value)
    instance.__dict__[self.name] = value

  # this is the new initializer:
  def __set_name__(self, owner, name):
    self.name = name


class Integer(Base):

  _root = True
  _descriptor_class = IntegerField

  def __init__(self, bitsize, signed=True, byteorder=None,
      **kwgs):
    self._bitsize = bitsize
    self._signed = signed
    self._byteorder = byteorder
    super().__init__(**kwgs)


class IntTest(Base)
  obj = Integer(2)


class Test(Base):
  c : Integer(2, default=0)
  a : Integer(4, True, readonly=True)

class Test2(Base):
  t : Test()

class Root(Base)


t = Test2()
