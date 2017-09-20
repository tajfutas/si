import datetime as _datetime_

from si.codec import Codec as _Codec_
from . import integer as _integer_

# References:
# Communication.cs 0917311 (#L3007-3022)
class DateCodec(_Codec_):

  bitsize = 24

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data):
    yy = _integer_.Int8u.decode(data[0:1])
    mm = _integer_.Int8u.decode(data[1:2])
    dd = _integer_.Int8u.decode(data[2:])
    now_year = _datetime_.datetime.now().year
    if yy <= now_year - 2000:
      yyyy = yy + 2000
    elif now_year - 2000 + 1 <= yy and yy <= 99:
      yyyy = yy + 1900
    return _datetime_.date(yyyy, mm, dd)
  #keep _datetime_
  #keep _integer_

  @classmethod
  @_Codec_.encodemethod
  def encode(cls, obj):
    yy = obj.year % 100
    return (_integer_.Int8u.encode(yy)
        + _integer_.Int8u.encode(obj.month)
        + _integer_.Int8u.encode(obj.day))
  #keep _integer_


del _Codec_
