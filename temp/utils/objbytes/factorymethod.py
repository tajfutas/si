#TODO: docstring

from functools import wraps as _wraps


def default(m):
  # TODO: improve, docstring
  @_wraps(m)
  def wrapped(cls, *args, **kwgs):
    if args and args[0] is None:
      return m(cls, *args[1:], **kwgs)
    else:
      return m(cls, *args, **kwgs)
  return wrapped


def default_if_arg_is_none(m):
  # TODO: improve, docstring
  @_wraps(m)
  def wrapped(cls, *args, **kwgs):
    if args and args[0] is None:
      return None
    else:
      return m(cls, *args, **kwgs)
  return wrapped


def none_if_first_arg_is_none(m):
  # TODO: improve, docstring
  @_wraps(m)
  def wrapped(cls, *args, **kwgs):
    if args and args[0] is None:
      return None
    else:
      return m(cls, *args, **kwgs)
  return wrapped
