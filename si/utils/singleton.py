class SingletonBase(type):

  def __new__(cls, typename, bases, ns):
    klass = super().__new__(cls, typename, bases, ns)
    klass.__new__ = None
    klass.__init__ = None
    klass.__call__ = None
    return klass

  def __str__(self):
    return self.__qualname__

  def __repr__(self):
    return self.__qualname__


class FalsySingletonBase(SingletonBase):

  def __bool__(self):
    return False


class NotSet(metaclass=FalsySingletonBase): pass


class Unknown(metaclass=FalsySingletonBase): pass
