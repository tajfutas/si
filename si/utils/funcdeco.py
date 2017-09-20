import functools as _functools_


def doublewrap(f):
  """
  A decorator decorator, allowing the decorator to be used as:
  @decorator(with, arguments, and=kwargs)
  or
  @decorator
  """
  # https://stackoverflow.com/a/14412901/2334951
  @_functools_.wraps(f)
  def new_dec(*args, **kwargs):
    if (len(args) == 1
        and len(kwargs) == 0
        and callable(args[0])
      ):
      # actual decorated function
      return f(args[0])
    else:
      # decorator arguments
      return lambda realf: f(realf, *args, **kwargs)
  return new_dec
#keep _functools_
