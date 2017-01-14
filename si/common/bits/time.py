import collections
import typing


import si
import si._datapart_decorators as deco


@deco.fixed_size(num_bits = 3)
class DayOfWeek(bytes):
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
  @classmethod
  def from_val(cls,
      val: typing.Union[si.DayOfWeek, str, int],
    ) -> 'cls':
    """
    Create a DayOfWeek instance from the given value

    Value can be a si.DayOfWeek enumeration, a string with the
    english name or abbreviation of the day, or an integer
    matching the SportIdent day of week standard
    (Sunday == 0, Monday == 1, ..., Saturday == 6).
    """
    if hasattr(val, 'value'):
      return cls([val.value])
    elif isinstance(val, str):
      return cls([si.DayOfWeek[val.title()].value])
    else:
      return cls([val])

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

  def val(self) -> si.DayOfWeek:
    "Return the corresponding si.DayOfWeek enumeration"
    return si.DayOfWeek(int.from_bytes(self, 'big'))


@deco.fixed_size(num_bits = 2)
class FourWeekCounterRelative(bytes):
  # TODO: more explanation
  """
  Four week counter relative stored in two bits.
  """
  # References:
  # PCPROG5 (pp. 17, 19)
  @classmethod
  def from_val(cls, val: int) -> 'cls':
    """
    Create a FourWeekCounterRelative instance from the given
    integer
    """
    return cls([val])

  def val(self) -> int:
    "Return the four week counter relative integer value"
    return int.from_bytes(self, 'big')


@deco.fixed_size(num_bits = 1)
class HalfDay(bytes):
  """Half day value in one bit

  0b0  AM
  0b1  PM
  """
  # References:
  # PCPROG5 (pp. 17, 19)
  @classmethod
  def from_val(cls,
      val: typing.Union[si.DayOfWeek, str, int],
    ) -> 'cls':
    """
    Create a HalfDay instance from the given value

    Value can be a si.HalfDay enumeration, a case insensitive
    period name string ("am", "PM", "a.m.", ...) or an integer
    (0 - am; 1 - pm).
    """
    if hasattr(val, 'value'):
      return cls([val.value])
    elif isinstance(val, str):
      normval = val.lower().replace('.','').replace(' ', '')
      return cls([si.HalfDay[normval].value])
    else:
      return cls([val])

  def val(self) -> si.HalfDay:
    "Return the corresponding si.HalfDay enumeration"
    return si.HalfDay(int.from_bytes(self, 'big'))


class TD_Parts(typing.NamedTuple):
    extra_bits: bytes
    four_week_counter_relative: FourWeekCounterRelative
    day_of_week: DayOfWeek
    half_day: HalfDay

@deco.fixed_size(num_bytes = 1)
class TD(bytes):
  """
  Four week counter relative, day of week, half day,
  and two extra bits in one byte.

  This byte is named as "TD" in the SI sources.
  """
  # References:
  # PCPROG5 (pp. 17, 19)
  @classmethod
  def from_parts(cls, td_parts: TD_Parts) -> 'cls':
    """
    Create a TD instance from the given TD_Parts

    TD_Parts should be a 4 bytes tuple (most likely a TD_Parts
    instance) with the following members:
    1. extra_bits: bytes from b'\X01' to b'\X03'
    2. four_week_counter_relative: FourWeekCounterRelative
    3. day_of_week: DayOfWeek
    4. half_day: HalfDay
    """
    return cls([
        (td_parts[0][0] << 6)
        + (td_parts[1][0] << 4)
        + (td_parts[2][0] << 1)
        + td_parts[3][0]
      ])

  def parts(self) -> TD_Parts:
    """
    Return the parts of the TD byte in four member TD_Parts
    tuple
    """
    intval = int.from_bytes(self, 'big')
    return TD_Parts(
        bytes([intval >> 6]),
        FourWeekCounterRelative.from_val(intval >> 4 & 0b11),
        DayOfWeek.from_val(intval >> 1 & 0b111),
        HalfDay.from_val(intval & 0b1),
      )


del deco
