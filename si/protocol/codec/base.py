

class BaseCodec:

  @classmethod
  def decode(cls, data):
    ...

  @classmethod
  def encode(cls, obj):
    ...

  @classmethod
  def classfactory(cls, name, *, bases=None, **dict_):
    bases = ((cls,) if bases is None else bases)
    return type(name, bases, dict_)

