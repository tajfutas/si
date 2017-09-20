def get(enum_cls, value):
  if isinstance(value, enum_cls):
    return value
  else:
    try:
      return enum_cls.__getitem__(value)
    except KeyError as exc:
      pass
    return enum_cls(value)
