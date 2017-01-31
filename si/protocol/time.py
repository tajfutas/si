import typing

import si.common
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
    return cls((0b111,))

  @classmethod
  @default_if_none
  def from_val(cls,
      val: typing.Union[si.common.DayOfWeek, str, int],
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
      v = [si.common.DayOfWeek[val.title()].value]
    return cls(v, _from=False)

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

  def val(self) -> si.common.DayOfWeek:
    "Return the corresponding si.DayOfWeek enumeration"
    return si.common.DayOfWeek(int.from_bytes(self, 'big'))


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
    return cls((0b00,))

  @classmethod
  @default_if_none
  def from_val(cls, val: int) -> 'cls':
    """
    Create a FourWeekCounterRelativeBits instance from the given
    integer
    """
    return cls([val], _from=False)

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
    return cls((0b0,))

  @classmethod
  @default_if_none
  def from_val(cls,
      val: typing.Union[si.common.DayOfWeek, str, int],
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
      v = [si.common.HalfDay[normval].value]
    return cls(v, _from=False)

  def val(self) -> si.common.HalfDay:
    "Return the corresponding si.HalfDay enumeration"
    return si.common.HalfDay(int.from_bytes(self, 'big'))


class TD_Parts(typing.NamedTuple):
  extra_bits: bytes
  four_week_counter_relative: FourWeekCounterRelativeBits
  day_of_week: DayOfWeekBits
  half_day: HalfDayBit


class TDByte(bytes2.Container):
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
