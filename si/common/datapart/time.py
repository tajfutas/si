import collections
import datetime
from enum import Enum
import struct
import typing

import si


class _docstring(Enum):
  day = "Day"
  hour = "Hours from midnight or noon according to pm value"
  isoweekday = (
  """
  Day of the week as per ISO 8601

  Monday == 1 ... Sunday == 7
  """)
  microsecond = "Subseconds in microseconds"
  minute = "Minutes"
  month = "Month"
  pm = (
  """
  24h counter

  AM == False, PM == True
  """)
  second = "Seconds"
  subsecond = "Subseconds in 1/256 seconds"
  total_second = (
  """
  Seconds from midnight or noon according to pm value
  """)
  weekcountrel = (
  """
  4 week counter relative

  More info: PCPROG5 (pp. 17)
  """)
  dayofweek = (
  """
  Day of Week in si.DayOfWeek enumeration as per
  SportIdent standard

  Sunday == 0, Monday == 1, ..., Saturday == 6
  """)
  year2000_2063 = "Year from 2000 to 2063"


class ImmutableWithNamedReadOnlyAttributes(type):
  """
  Metaclass which populates the instance classes with read only
  property descriptors. The sequence of attribute names should
  be defined as ::cls._NAMED_ATTR_NAMES::. Optionally
  ::cls._NAMED_ATTR_DOCS:: can contain the dosstrings of the
  properties.

  It is up to the instances to provide sequences of values with
  same length as ::self._named_attrs::.

  Only getter functions will be added so this metaclass could
  be used primary with immutable objects.
  """
  def __init__(cls, name, bases, nmspc):
    super().__init__(name, bases, nmspc)
    has_docs = hasattr(cls, '_NAMED_ATTR_DOCS')
    for i, attrname in enumerate(cls._NAMED_ATTR_NAMES):
      setattr(cls, attrname,
          property(lambda self, i=i: self._named_attrs[i],
              doc=(cls._NAMED_ATTR_DOCS[i] if has_docs
                  and cls._NAMED_ATTR_DOCS else None)
            )
        )


class BaseTime(bytes,
    metaclass=ImmutableWithNamedReadOnlyAttributes):
  """
  Baseclass for punch time formats. Subclass of bytes.
  """

  #: Private constant! Must be defined in subclasses.
  #: Indicates the expected length of the data.
  _SIZE = 0

  #: Private constant! Must be defined in subclasses.
  #: A tuple of strings with the name of the attributes which
  #: will be added with their corresponding values (and
  #: docstrings) to the instances.
  #: Cooperates with _get_named_attrs_vals() (values) and the
  #: optional _NAMED_ATTR_DOCS (docstrings).
  _NAMED_ATTR_NAMES = ()

  #: Private constant! Must be defined in subclasses.
  #: A tuple of strings with the docstrings of the attributes
  #: which will be added with their corresponding names and
  #: values to the instances.
  #: Cooperates with _NAMED_ATTR_NAMES (names) and
  #: _get_named_attrs_vals() (values).
  _NAMED_ATTR_DOCS = ()

  def __new__(cls, seq):
    if len(seq) != cls._SIZE:
      efs = 'invalid sequence length (expected {}): {}'
      raise TypeError(efs.format(cls._SIZE, len(seq)))
    instance = super().__new__(cls, seq)
    named_attrs = instance._get_named_attrs_vals()
    instance._named_attrs = named_attrs
    return instance

  def _get_named_attrs_vals(self):
    """
    Private function! Should be defined in subclasses.

    Returns a tuple of the values of the attributes which will
    be added with their corresponding names (and docstring) to
    the instances.
    Cooperates with _NAMED_ATTR_NAMES (names) and the optional
    _NAMED_ATTR_DOCS (docstrings).
    """
    return ()


class FourBytesTime1(BaseTime):
  """
  Class for punch times stored in four bytes.

  These bytes are named as following by the official sources:
  * TD, TH, TL, TSS

  Note that error codes are not yet supported!

  More info:
  PCPROG5 (pp. 11 /SW 5.54-/, 17)
  """
  _SIZE = 4
  _NAMED_ATTR_NAMES = (
      'weekcountrel',
      'dayofweek',
      'pm',
      'hour',
      'minute',
      'second',
      'subsecond',
      'isoweekday',
      'total_second',
      'microsecond',
    )
  _NAMED_ATTR_DOCS = (
      _docstring.weekcountrel.value,
      _docstring.dayofweek.value,
      _docstring.pm.value,
      _docstring.hour.value,
      _docstring.minute.value,
      _docstring.second.value,
      _docstring.subsecond.value,
      _docstring.isoweekday.value,
      _docstring.total_second.value,
      _docstring.microsecond.value,
    )

  @staticmethod
  def _normalize_params(
      dayofweek: int,
      pm: bool,
      hour: int,
      minute: int,
      second: int,
      subsecond: int
    ) -> typing.Tuple[int, bool, int, int, int, int]:
    """
    Private function!

    Moves on the next possible higher parameter when subsecond
    is 256. This can be easily necessary when instatntiated from
    a datetime object.

    Returns the normalized time parameters in the same order.
    """
    while subsecond >= 256:
      subsecond -= 256
      second += 1
      if second == 60:
        second = 0
        minute += 1
        if minute == 60:
          minute = 0
          hour += 1
          if hour == 12:
            if pm:
              pm = False
              dayofweek = (dayofweek + 1) % 7
            else:
              pm = True
            hour = 0
    return dayofweek, pm, hour, minute, second, subsecond

  @classmethod
  def from_params(cls,
      weekcountrel: int,
      dayofweek: int,
      pm: bool,
      hour: int,
      minute: int,
      second: int,
      subsecond: int
    ) -> 'cls':
    """
    Creates an instance from the time parameters.
    """
    assert weekcountrel in range(5)
    assert dayofweek in range(7)
    assert pm in range(2)
    assert hour in range(12)
    assert minute in range(60)
    assert second in range(60)
    assert subsecond in range(256)
    TD = (weekcountrel << 4) + (dayofweek << 1) + pm
    total_second = 3600 * hour + 60 * minute + second
    TH, TL = struct.pack('>H', total_second)
    TSS = subsecond
    return cls(bytes((TD, TH, TL, TSS)))

  @classmethod
  def from_datetime(cls,
      T: datetime.datetime = None,
      weekcountrel: int = 0,
    ) -> 'cls':
    """
    Creates an instance from an optional datetime.datetime
    (default PC time) object and the optional weakcountrel
    (four weak couter relative) parameter (default 0).
    """
    if T is None:
      T = datetime.datetime.now()
    dayofweek = T.isoweekday() % 7
    pm, hour = divmod(T.hour, 12)
    subsecond = round(T.microsecond * 256 / 1000000)
    return cls.from_params(weekcountrel, *cls._normalize_params(
        dayofweek, pm, hour, T.minute, T.second, subsecond))

  @classmethod
  def from_timedelta(cls,
      dayofweek: typing.Union[si.DayOfWeek, str, int],
      Td: datetime.timedelta,
      weekcountrel: int = 0
    ) -> 'cls':
    """
    Creates an instance from day of week, a datetime.timedelta
    object, and an optional weakcountrel (four weak couter
    relative) parameter (default 0).

    dayofweek can be either a si.DayOfWeek enumeration,
    a string, or an integer
    (Sunday: 0, Monday: 1, ..., Saturday: 6).
    """
    dayofweek = ensure_dayofweek_enum(dayofweek)
    assert (datetime.timedelta(0) <= Td < datetime.timedelta(1))
    pm = (True if 12 * 60 * 60 < Td.seconds else False)
    hour = Td.seconds // 3600
    minute = Td.seconds % 3600 // 60
    second = Td.seconds %  60
    subsecond = round(Td.microseconds * 256 / 1000000)
    if subsecond == 256:
      second += 1
      subsecond = 0
    return cls.from_params(weekcountrel,
        *cls._normalize_params(
            dayofweek, pm, hour, minute, second, subsecond)
      )

  def __str__(self):
    fstr = '<T4.1: W{} D{} {} {:0>2}:{:0>2}:{:0>2}.{:0>3}/256>'
    return fstr.format(
        self.weekcountrel,
        self.dayofweek.value,
        ('PM' if self.pm else 'AM'),
        self.hour,
        self.minute,
        self.second,
        self.subsecond,
      )

  def _get_named_attrs_vals(self):
    TD = self[0]
    TH = self[1]
    TL = self[2]
    TSS = self[3]
    weekcountrel = TD >> 4 & 0b11
    dayofweek = si.DayOfWeek(TD >> 1 & 0b1110)
    isoweekday = dayofweek2isoweekday(dayofweek)
    pm = bool(TD & 0b1)
    total_second = struct.unpack('>H', bytes([TH, TL]))[0]
    hour = total_second // 3600
    minute = total_second % 3600 // 60
    second = total_second % 60
    subsecond = TSS
    microsecond = round(subsecond * 1000000 / 256)
    return (
        weekcountrel,
        dayofweek,
        pm,
        hour,
        minute,
        second,
        subsecond,
        isoweekday,
        total_second,
        microsecond,
      )

  def timedelta(self) -> datetime.timedelta:
    "Time elapsed from midnight"
    return datetime.timedelta(0,
        3600 * 12 * self.pm + self.total_second,
        self.microsecond)


class FiveBytesTime1(BaseTime):
  """
  Class for punch times stored in four bytes.

  These bytes are named as following by the official sources:
  * DATE1, DATE0, TH, TL, MS

  More info:
  PCPROG5 (pp. 11 /SW 5.55+/)
  """
  _SIZE = 5
  _NAMED_ATTR_NAMES = (
      'year',
      'month',
      'day',
      'pm',
      'hour',
      'minute',
      'second',
      'subsecond',
      'dayofweek',
      'isoweekday',
      'total_second',
      'microsecond',
    )
  _NAMED_ATTR_DOCS = (
      _docstring.year2000_2063.value,
      _docstring.month.value,
      _docstring.day.value,
      _docstring.pm.value,
      _docstring.hour.value,
      _docstring.minute.value,
      _docstring.second.value,
      _docstring.subsecond.value,
      _docstring.dayofweek.value,
      _docstring.isoweekday.value,
      _docstring.total_second.value,
      _docstring.microsecond.value,
    )

  @staticmethod
  def _normalize_params(
      year: int,
      month: int,
      day: int,
      pm: bool,
      hour: int,
      minute: int,
      second: int,
      subsecond: int
    ) -> typing.Tuple[int, int, int, bool, int, int, int, int]:
    """
    Private function!

    Moves on the next possible higher parameter when subsecond
    is 256. This can be easily necessary when instatntiated from
    a datetime object.

    Returns the normalized time parameters in the same order.
    """
    T = datetime.datetime(year, month, day, 12 * pm + hour,
        minute, second)
    seconds, subsecond = divmod(subsecond, 256)
    T += datetime.timedelta(seconds=seconds)
    pm, hour = divmod(T.hour, 12)
    return (T.year, T.month, T.day, pm, hour, minute, second,
        subsecond)

  @classmethod
  def from_params(cls,
      year: int,
      month: int,
      day: int,
      pm: bool,
      hour: int,
      minute: int,
      second: int,
      subsecond: int
    ) -> 'cls':
    """
    Creates an instance from the time parameters.
    """
    # References:
    # PCPROG5 (pp. 11 /SW 5.55+/)
    # Communication.cs 9e2e1aa (#L1958-L2323)

    # <- PCPROG5: "bit 7-2  6 bit year  0--64 part of year"
    # -> unclear; contradiction: 64 takes 7 bit to store
    # <- Communication: "num4 = (num & 64512) >> 10;
    #     num4 += 2000;"
    # -> format: 2000 + value in 0--63 defines year
    assert year in range(2000, 2064)
    assert month in range(13)
    assert day in range(32)
    assert pm in range(2)
    assert hour in range(12)
    assert minute in range(60)
    assert second in range(60)
    assert subsecond in range(256)
    DATE1 = ((year-2000) << 2) + (month >> 2 & 0b11)
    DATE0 = ((month & 0b11) << 6) + (day << 1) + pm
    total_second = 3600 * hour + 60 * minute + second
    TH, TL = struct.pack('>H', total_second)
    MS = subsecond
    return cls(bytes((DATE1, DATE0, TH, TL, MS)))

  @classmethod
  def from_datetime(cls,
      T: datetime.datetime = None,
    ) -> 'cls':
    """
    Creates an instance from an optional datetime.datetime
    (default PC time) object.
    """
    if T is None:
      T = datetime.datetime.now()
    pm, hour = divmod(T.hour, 12)
    subsecond = round(T.microsecond * 256 / 1000000)
    return cls.from_params(*cls._normalize_params(
        T.year, T.month, T.day,
        pm, hour, T.minute, T.second, subsecond))

  def _get_named_attrs_vals(self):
    DATE1 = self[0]
    DATE0 = self[1]
    TH = self[2]
    TL = self[3]
    MS = self[4]
    year = 2000 + (DATE1 >> 2)
    month = (DATE1 << 2 & 0b1100) + (DATE0 >> 6)
    day = DATE0 >> 1 & 0b11111
    pm = bool(DATE0 & 0b1)
    total_second = struct.unpack('>H', bytes([TH, TL]))[0]
    hour = total_second // 3600
    minute = total_second % 3600 // 60
    second = total_second % 60
    subsecond = MS
    microsecond = round(subsecond * 1000000 / 256)
    date = datetime.date(year, month, day)
    isoweekday = date.isoweekday()
    dayofweek = isoweekday2dayofweek(isoweekday)
    return (
        year,
        month,
        day,
        pm,
        hour,
        minute,
        second,
        subsecond,
        dayofweek,
        isoweekday,
        total_second,
        microsecond,
      )

  def datetime(self) -> datetime.datetime:
    "Time"
    return datetime.datetime(
        self.year, self.month, self.day,
        self.hour, self.minute, self.second, self.microsecond)


class SevenBytesTime(BaseTime):
  """
  Class for punch times stored in four bytes.

  These bytes are named as following by the official sources:
  * YY, MM, DD, TWD, TH, TL, TSS
  * CD2, CD1, CD0, TD, TH, TL, TSS
  .

  Source: PCPROG5 (pp. 17)
  """
  _SIZE = 7

  ## TODO...


def dayofweek2isoweekday(
    dayofweek: typing.Union[si.DayOfWeek, str, int]
  ) -> int:
  """
  Converts SI day of week to ISO weekday

  Returns day of the week as per ISO 8601 standard
  (Monday == 1 ... Sunday == 7) from the given SportIdent
  day of week value
  (Sunday == 0, Monday == 1, ..., Saturday == 6).
  """
  dayofweek = ensure_dayofweek_enum(dayofweek)
  if dayofweek.value == 7:
    return None
  else:
    return (dayofweek.value if 0 < dayofweek.value else 7)


def ensure_dayofweek_enum(
    dayofweek: typing.Union[si.DayOfWeek, str, int]
  ) -> si.DayOfWeek:
  """
  Ensures si.DayOfWeek

  Returns an si.DayOfWeek enumeration from the given value,
  be it an existing si.DayOfWeek, a string with the english name
  or abbreviation of the day, or an integer matching the
  SportIdent day of week standard
  (Sunday == 0, Monday == 1, ..., Saturday == 6).
  """
  if hasattr(dayofweek, 'value'):
    return si.DayOfWeek(dayofweek.value)
  elif isinstance(dayofweek, str):
    return si.DayOfWeek[dayofweek.title()]
  else:
    return si.DayOfWeek(dayofweek)


def isoweekday2dayofweek(
    isoweekday: int
  ) -> si.DayOfWeek:
  """
  Converts SI day of week to ISO weekday

  Returns day of week in si.DayOfWeek enumeration as per
  SportIdent standard
  (Sunday == 0, Monday == 1, ..., Saturday == 6)
  from the given day of the week as per ISO 8601
  standard (Monday == 1 ... Sunday == 7).
  """
  dayofweek = isoweekday
  if dayofweek == 7:
    dayofweek = 0
  return si.DayOfWeek(dayofweek)
