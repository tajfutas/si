class SingletonBase(type):

  def __new__(cls, typename, bases, ns):
    klass = super().__new__(cls, typename, bases, ns)
    klass.__new__ = None
    klass.__init__ = None
    klass.__call__ = None
    return klass

  def __repr__(self):
    return self.__qualname__


class NotSet(metaclass=SingletonBase): pass


class Unknown(metaclass=SingletonBase): pass
