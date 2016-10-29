import collections
import datetime
from enum import Enum
import struct
import typing


class Weekday(Enum):
  """
  Day of week enumeration.
  Sunday == 0 ... Saturday == 6

  Source: PCPROG5 (p. 17)
  """
  Sunday = 0
  Monday = 1
  Tuesday = 2
  Wednesday = 3
  Thursday = 4
  Friday = 5
  Saturday = 6
  sunday = 0
  monday = 1
  tuesday = 2
  wednesday = 3
  thursday = 4
  friday = 5
  saturday = 6
  SUNDAY = 0
  MONDAY = 1
  TUESDAY = 2
  WEDNESDAY = 3
  THURSDAY = 4
  FRIDAY = 5
  SATURDAY = 6


class ImmutableWithNamedReadOnlyAttributes(type):
  """
  Metaclass which populates the instance classes with read only
  property descriptors. The sequence of attribute names should
  be defined as ::cls._NAMED_ATTRS::. Optionally
  ::cls._NAMED_ATTR_DOCS:: can contain the dosstrings of the
  properties.

  It is up to the instances to provide sequences of values with
  same length as ::self._named_attrs::.

  Only getter functions will be added so this metaclass could
  be used primary with immutable objects.
  """
  def __init__(cls, name, bases, nmspc):
    super().__init__(name, bases, nmspc)
    has_docs = hasattr(cls, '._NAMED_ATTR_DOCS')
    for i, attrname in enumerate(cls._NAMED_ATTRS):
      setattr(cls, attrname,
          property(lambda self, i=i: self._named_attrs[i],
          doc=(cls._NAMED_ATTR_DOCS[i] if has_docs else None)
          ))


class PunchTime(bytes,
    metaclass=ImmutableWithNamedReadOnlyAttributes):

  _SIZE = 0
  _NAMED_ATTRS = ()

  def __new__(cls, seq):
    assert len(seq) == cls._SIZE
    instance = super().__new__(cls, seq)
    named_attrs = instance._get_named_attrs()
    instance._named_attrs = named_attrs
    return instance

  def _get_named_attrs(self):
    raise NotImplementedError()


class FourBytesPunchTime(PunchTime):

  _SIZE = 4
  _NAMED_ATTRS = (
      'weekcountrel',
      'weekday',
      'isoweekday',
      'pm',
      'total_seconds',
      'hour',
      'minute',
      'second',
      'subsecond',
      'microsecond',
      )

  @staticmethod
  def _normalize_params(weekday, pm, hour, minute, second,
      subsecond):
    if subsecond == 256:
      second += 1
      subsecond = 0
      if second == 60:
        minute += 1
        second = 0
        if minute == 60:
          hour += 1
          minute = 0
          if hour == 12:
            if pm:
              weekday = (weekday + 1) % 7
              pm = False
            else:
              pm = True
            hour = 0
    return weekday, pm, hour, minute, second, subsecond

  @classmethod
  def from_params(cls,
      weekcountrel: int,
      weekday: int,
      pm: bool,
      hour: int,
      minute: int,
      second: int,
      subsecond: int
      ) -> 'cls':
    assert weekcountrel in range(5)
    assert weekday in range(7)
    assert pm in range(2)
    assert hour in range(12)
    assert minute in range(60)
    assert second in range(60)
    assert subsecond in range(256)
    TD = (weekcountrel << 4) + (weekday << 1) + pm
    total_seconds = 3600 * hour + 60 * minute + second
    TH, TL = struct.pack('>H', total_seconds)
    TSS = subsecond
    return cls(bytes((TD, TH, TL, TSS)))

  @classmethod
  def from_datetime(cls,
      T: datetime.datetime = None,
      weekcountrel: int = 0,
      ) -> 'cls':
    if T is None:
      T = datetime.datetime.now()
    weekday = T.isoweekday() % 7
    pm, hour = divmod(T.hour, 12)
    minute = T.minute
    second = T.second
    subsecond = round(T.microsecond * 256 / 1000000)
    return cls.from_params(weekcountrel,
        *cls._normalize_params(weekday, pm, hour, minute,
            second, subsecond)
        )

  @classmethod
  def from_timedelta(cls,
      weekday: typing.Union[Weekday, str, int],
      Td: datetime.timedelta,
      weekcountrel: int = 0
      ) -> 'cls':
    if hasattr(weekday, 'value'):  # for Weekday Enum
      weekday = weekday.value
    elif isinstance(weekday, str):
      weekday = Weekday[weekday].value
    else:
      weekday = Weekday(weekday).value
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
        *cls._normalize_params(weekday, pm, hour, minute,
            second, subsecond)
        )

  def __str__(self):
    fstr = '<PT4: W{} D{} {} {:0>2}:{:0>2}:{:0>2}.{:0>3}/256>'
    return fstr.format(
        self.weekcountrel,
        self.weekday.value,
        ('PM' if self.pm else 'AM'),
        self.hour,
        self.minute,
        self.second,
        self.subsecond,
        )

  def _get_named_attrs(self):
    TD = self[0]
    TH = self[1]
    TL = self[2]
    TSS = self[3]
    weekcountrel = (TD & 0b00110000) >> 4
    weekday = Weekday((TD & 0b00001110) >> 1)
    isoweekday = (weekday.value if 0 < weekday.value else 7)
    pm = bool(TD & 0b00000001)
    total_seconds = struct.unpack('>H', bytes([TH, TL]))[0]
    hour = total_seconds // 3600
    minute = total_seconds % 3600 // 60
    second = total_seconds % 60
    subsecond = TSS
    microsecond = round(subsecond * 1000000 / 256)
    return (weekcountrel, weekday, isoweekday, pm,
        total_seconds, hour, minute, second, subsecond,
        microsecond)

  def timedelta(self) -> datetime.timedelta:
    return datetime.timedelta(0,
        3600 * 12 * self.pm + self.total_seconds,
        self.microsecond)
