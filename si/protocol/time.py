import typing

import si.common as _common
from si.utils import objbytes


class DayOfWeekBits(objbytes.base.Bits):
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

  _bitsize = 0o3

  @classmethod
  @objbytes.factorymethod.default
  def default(cls, *,
      check_bitsize:bool=False, **kwgs
    ) -> 'cls':
    return cls((0b111,), check_bitsize=False,
        factory_meth=False)

  @classmethod
  @objbytes.factorymethod.default_if_arg_is_none
  def from_obj(cls,
      obj: typing.Union[None, _common.DayOfWeek, str, int],
      **kwgs
    ) -> 'cls':
    """
    Create a DayOfWeekBits instance from the given value

    Value can be a si.DayOfWeek enumeration, a string with the
    english name or abbreviation of the day, or an integer
    matching the SportIdent day of week standard
    (Sunday == 0, Monday == 1, ..., Saturday == 6).
    """
    o = [obj]
    if hasattr(obj, 'value'):
      o = [obj.value]
    elif isinstance(obj, str):
      o = [_common.DayOfWeek[obj.title()].value]
    kwgs['factory_meth'] = False
    return cls(o, **kwgs)

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

  def obj(self) -> _common.DayOfWeek:
    "Return the corresponding si.DayOfWeek enumeration"
    return _common.DayOfWeek(int.from_bytes(self, 'big'))


class FourWeekCounterRelativeBits(objbytes.base.Bits):
  # TODO: more explanation
  """
  Four week counter relative stored in two bits.
  """
  # References:
  # PCPROG5 (pp. 17, 19)

  _bitsize = 0o2

  @classmethod
  @objbytes.factorymethod.default
  def default(cls, *,
      check_bitsize:bool=False, **kwgs
    ) -> 'cls':
    return cls((0b00,), check_bitsize=False,
        factory_meth=False)

  @classmethod
  @objbytes.factorymethod.default_if_arg_is_none
  def from_obj(cls,
      obj: typing.Union[None, int],
      **kwgs
    ) -> 'cls':
    """
    Create a FourWeekCounterRelativeBits instance from the given
    integer
    """
    kwgs['factory_meth'] = False
    return cls([obj], **kwgs)

  def obj(self) -> int:
    "Return the four week counter relative integer value"
    return int.from_bytes(self, 'big')


class HalfDayBit(objbytes.base.Bits):
  """Half day value in one bit

  0b0  AM
  0b1  PM
  """
  # References:
  # PCPROG5 (pp. 17, 19)

  _bitsize = 0o1

  @classmethod
  @objbytes.factorymethod.default
  def default(cls, *,
      check_bitsize:bool=False, **kwgs
    ) -> 'cls':
    return cls((0b0,), check_bitsize=False, factory_meth=False)

  @classmethod
  @objbytes.factorymethod.default_if_arg_is_none
  def from_obj(cls,
      obj: typing.Union[None, _common.DayOfWeek, str, int],
      **kwgs
    ) -> 'cls':
    """
    Create a HalfDayBit instance from the given value

    Value can be a si.HalfDay enumeration, a case insensitive
    period name string ("am", "PM", "a.m.", ...) or an integer
    (0 - am; 1 - pm).
    """
    o = [obj]
    if hasattr(obj, 'value'):
      o = [obj.value]
    elif isinstance(obj, str):
      s_normal = obj.lower().replace('.','').replace(' ', '')
      o = [_common.HalfDay[s_normal].value]
    kwgs['factory_meth'] = False
    return cls(o, **kwgs)

  def obj(self) -> _common.HalfDay:
    "Return the corresponding si.HalfDay enumeration"
    return _common.HalfDay(int.from_bytes(self, 'big'))


class TDByte(objbytes.types.collections.NamedTupleBytes):
  pad = objbytes.types.pad.PadBits(2)
  fourweekcrel = FourWeekCounterRelativeBits
  dayofweek = DayOfWeekBits
  halfday = HalfDayBit


del typing

del objbytes
