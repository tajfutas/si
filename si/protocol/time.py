import typing

import si.common as _common
from si.utils import bytes2
from si.utils.methdeco import default_if_none

class DayOfWeekBits(bytes2.Bits):
  """
  Day of week stored in three bits.

  0b000  Sunday
  0b001  Monday
  0b010  Tuesday
  0b011  Wednesday
  0b100  Thursday
  0b101  Friday
  0b110  Saturday
  0b111  Not Set or Invalid
  """
  # References:
  # PCPROG5 (pp. 17, 19)
  # SPORTident 9e291aa \DayOfWeek.cs

  _OCTETS = 0o3

  @classmethod
  def default(cls) -> 'cls':
    return cls((0b111,), _from=False, _check_octets=False)

  @classmethod
  @default_if_none
  def from_val(cls,
      val: typing.Union[_common.DayOfWeek, str, int],
      **kwgs
    ) -> 'cls':
    """
    Create a DayOfWeekBits instance from the given value

    Value can be a si.DayOfWeek enumeration, a string with the
    english name or abbreviation of the day, or an integer
    matching the SportIdent day of week standard
    (Sunday == 0, Monday == 1, ..., Saturday == 6).
    """
    v = [val]
    if hasattr(val, 'value'):
      v = [val.value]
    elif isinstance(val, str):
      v = [_common.DayOfWeek[val.title()].value]
    kwgs['_from'] = False
    return cls(v, **kwgs)

  def isoweekday(self) -> int:
    """"
    Return day of the week as per ISO 8601 standard

    (Monday == 1 ... Sunday == 7)

    Return None if Not Set or Invalid
    """
    int_value = int.from_bytes(self, 'big')
    if int_value == 7:
      return None
    else:
      return (int_value if 0 < int_value else 7)

  def val(self) -> _common.DayOfWeek:
    "Return the corresponding si.DayOfWeek enumeration"
    return _common.DayOfWeek(int.from_bytes(self, 'big'))


class FourWeekCounterRelativeBits(bytes2.Bits):
  # TODO: more explanation
  """
  Four week counter relative stored in two bits.
  """
  # References:
  # PCPROG5 (pp. 17, 19)

  _OCTETS = 0o2

  @classmethod
  def default(cls) -> 'cls':
    return cls((0b00,), _from=False, _check_octets=False)

  @classmethod
  @default_if_none
  def from_val(cls, val: int, **kwgs) -> 'cls':
    """
    Create a FourWeekCounterRelativeBits instance from the given
    integer
    """
    kwgs['_from'] = False
    return cls([val], **kwgs)

  def val(self) -> int:
    "Return the four week counter relative integer value"
    return int.from_bytes(self, 'big')


class HalfDayBit(bytes2.Bits):
  """Half day value in one bit

  0b0  AM
  0b1  PM
  """
  # References:
  # PCPROG5 (pp. 17, 19)

  _OCTETS = 0o1

  @classmethod
  def default(cls) -> 'cls':
    return cls((0b0,), _from=False, _check_octets=False)

  @classmethod
  @default_if_none
  def from_val(cls,
      val: typing.Union[_common.DayOfWeek, str, int],
      **kwgs
    ) -> 'cls':
    """
    Create a HalfDayBit instance from the given value

    Value can be a si.HalfDay enumeration, a case insensitive
    period name string ("am", "PM", "a.m.", ...) or an integer
    (0 - am; 1 - pm).
    """
    v = [val]
    if hasattr(val, 'value'):
      v = [val.value]
    elif isinstance(val, str):
      normval = val.lower().replace('.','').replace(' ', '')
      v = [_common.HalfDay[normval].value]
    kwgs['_from'] = False
    return cls(v, **kwgs)

  def val(self) -> _common.HalfDay:
    "Return the corresponding si.HalfDay enumeration"
    return _common.HalfDay(int.from_bytes(self, 'big'))


class TDByte(bytes2.DictBytes):
  _OCTETS = 0o10
  _ITEMS = (
      ("pad", bytes2.PadBits(2)),
      ("fourweekcrel", FourWeekCounterRelativeBits),
      ("dayofweek", DayOfWeekBits),
      ("halfday", HalfDayBit),
    )


del typing

del bytes2
del default_if_none
