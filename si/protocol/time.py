import typing

from si import si as _si
from . import _base
from . import _decorator


class DayOfWeekBits(_base.Bits):
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
    return cls((0b111,))

  @classmethod
  def from_val(cls,
      val: typing.Union[_si.DayOfWeek, str, int],
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
      v = [_si.DayOfWeek[val.title()].value]
    return cls(v, _from_val=True)

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

  def val(self) -> _si.DayOfWeek:
    "Return the corresponding si.DayOfWeek enumeration"
    return _si.DayOfWeek(int.from_bytes(self, 'big'))


class FourWeekCounterRelativeBits(_base.Bits):
  # TODO: more explanation
  """
  Four week counter relative stored in two bits.
  """
  # References:
  # PCPROG5 (pp. 17, 19)

  _OCTETS = 0o2

  @classmethod
  def default(cls) -> 'cls':
    return cls((0b00,))

  @classmethod
  def from_val(cls, val: int) -> 'cls':
    """
    Create a FourWeekCounterRelativeBits instance from the given
    integer
    """
    return cls([val], _from_val=True)

  def val(self) -> int:
    "Return the four week counter relative integer value"
    return int.from_bytes(self, 'big')


class HalfDayBit(_base.Bits):
  """Half day value in one bit

  0b0  AM
  0b1  PM
  """
  # References:
  # PCPROG5 (pp. 17, 19)

  _OCTETS = 0o1

  @classmethod
  def default(cls) -> 'cls':
    return cls((0b0,))

  @classmethod
  def from_val(cls,
      val: typing.Union[_si.DayOfWeek, str, int],
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
      v = [_si.HalfDay[normval].value]
    return cls(v, _from_val=True)

  def val(self) -> _si.HalfDay:
    "Return the corresponding si.HalfDay enumeration"
    return _si.HalfDay(int.from_bytes(self, 'big'))


class TD_Parts(typing.NamedTuple):
  extra_bits: bytes
  four_week_counter_relative: FourWeekCounterRelativeBits
  day_of_week: DayOfWeekBits
  half_day: HalfDayBit


class TDByte(_base.Container):
  _OCTETS = 0o10
  _ITEMS = (
      ("pad", _base.PadBits(0o2)),
      ("fourweekcrel", FourWeekCounterRelativeBits),
      ("dayofweek", DayOfWeekBits),
      ("halfday", HalfDayBit),
    )


del typing

del _base
del _decorator
