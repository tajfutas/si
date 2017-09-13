import datetime as _datetime

from . import base as _base
from . import integer as _integer

# References:
# Communication.cs 0917311 (#L3007-3022)
class DateCodec(_base.BaseCodec):

  bitsize = 24

  @classmethod
  def decode(cls, data):
    yy = _integer.Int8u.decode(data[0:1])
    mm = _integer.Int8u.decode(data[1:2])
    dd = _integer.Int8u.decode(data[2:])
    now_year = _datetime.datetime.now().year
    if yy <= now_year - 2000:
      yyyy = yy + 2000
    elif now_year - 2000 + 1 <= yy and yy <= 99:
      yyyy = yy + 1900
    return _datetime.date(yyyy, mm, dd)

  @classmethod
  def encode(cls, obj):
    yy = obj.year % 100
    return (_integer.Int8u.encode(yy)
        + _integer.Int8u.encode(obj.month)
        + _integer.Int8u.encode(obj.day))


del _base
