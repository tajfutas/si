import collections
import datetime
from enum import Enum
import struct
import typing
import warnings


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
  Sun = 0
  Mon = 1
  Tue = 2
  Wed = 3
  Thu = 4
  Fri = 5
  Sat = 6
  sun = 0
  mon = 1
  tue = 2
  wed = 3
  thu = 4
  fri = 5
  sat = 6
  SUN = 0
  MON = 1
  TUE = 2
  WED = 3
  THU = 4
  FRI = 5
  SAT = 6
  Su = 0
  Mo = 1
  Tu = 2
  We = 3
  Th = 4
  Fr = 5
  Sa = 6
  su = 0
  mo = 1
  tu = 2
  we = 3
  th = 4
  fr = 5
  sa = 6
  SU = 0
  MO = 1
  TU = 2
  WE = 3
  TH = 4
  FR = 5
  SA = 6


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
          ))


class BasePunchTime(bytes,
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


class FourBytesPunchTime(BasePunchTime):
  """
  Class for punch times stored in four bytes.

  These bytes are named as following by the official sources:
  * TD, TH, TL, TSS

  Note that error codes are not yet supported!

  Source: PCPROG5 (pp. 11 /SW 5.54-/, 17)
  """
  _SIZE = 4
  _NAMED_ATTR_NAMES = (
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
  _NAMED_ATTR_DOCS = (
      """
      4 week counter relative

      More info: PCPROG5 (pp. 17)
      """,
      """
      Day of Week in Weekday enumeration as per SportIdent
      standard.
      Sunday == 0, Monday == 1, ..., Saturday == 6

      More info: PCPROG5 (pp. 17)
      """,
      """
      Day of the week as per ISO 8601.
      Monday == 1 ... Sunday == 7
      """,
      """
      24h counter.
      AM == False, PM == True
      """,
      """
      Time elapsed from midnight or noon according to pm value
      (False, True respectively), in seconds.
      """,
      """
      Time elapsed from midnight or noon according to pm value
      (False, True respectively), in hours.
      """,
      """
      Time elapsed from hour, in minutes.
      """,
      """
      Time elapsed from minute, in seconds.
      """,
      """
      Subseconds in 1/256 seconds.
      """,
      """
      Subseconds in microseconds (1/10^6 seconds).
      """,
      )

  @staticmethod
  def _normalize_params(
      weekday: int,
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
              weekday = (weekday + 1) % 7
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
    """
    Creates an instance from the time parameters.

    More info: PCPROG5 (pp. 17)
    """
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
    """
    Creates an instance from an optional datetime.datetime
    (default PC time) object and the optional weakcountrel
    (four weak couter relative) parameter (default 0).

    More info: PCPROG5 (pp. 17)
    """
    if T is None:
      T = datetime.datetime.now()
    weekday = T.isoweekday() % 7
    pm, hour = divmod(T.hour, 12)
    subsecond = round(T.microsecond * 256 / 1000000)
    return cls.from_params(weekcountrel, *cls._normalize_params(
        weekday, pm, hour, T.minute, T.second, subsecond))

  @classmethod
  def from_timedelta(cls,
      weekday: typing.Union[Weekday, str, int],
      Td: datetime.timedelta,
      weekcountrel: int = 0
      ) -> 'cls':
    """
    Creates an instance from weekday, a datetime.timedelta
    object, and an optional weakcountrel (four weak couter
    relative) parameter (default 0).

    weekday can be either a Weekday enumeration, a string, or an
    integer (Sunday: 0, Monday: 1, ..., Saturday: 6).

    More info: PCPROG5 (pp. 17)
    """
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

  def _get_named_attrs_vals(self):
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
    return (
      weekcountrel,
      weekday,
      isoweekday,
      pm,
      total_seconds,
      hour,
      minute,
      second,
      subsecond,
      microsecond,
      )

  def timedelta(self) -> datetime.timedelta:
    """Time elapsed from midnight."""
    return datetime.timedelta(0,
        3600 * 12 * self.pm + self.total_seconds,
        self.microsecond)


class FiveBytesPunchTime(BasePunchTime):
  """
  Class for punch times stored in four bytes.

  These bytes are named as following by the official sources:
  * DATE1, DATE0, TH, TL, MS

  Source: PCPROG5 (pp. 11 /SW 5.55+/)
  """
  _SIZE = 5

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
      ) -> typing.Tuple[int, int, int, bool, int, int, int,
          int]:
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

    More info: PCPROG5 (pp. 11)
    """
    # PCPROG5: "bit 7-2  6 bit year  0--64 part of year"
    # unclear; contradiction: 64 takes 7 bit to store
    # anticipated format: 2000 + value in 0--63 defines year
    assert year in range(2000, 2064)
    assert month in range(13)
    assert day in range(32)
    assert pm in range(2)
    assert hour in range(12)
    assert minute in range(60)
    assert second in range(60)
    assert subsecond in range(256)
    DATE1 = ((year-2000) << 2) + ((month & 12) >> 2)
    DATE0 = ((month & 12) << 4) + (day << 1) + pm
    total_seconds = 3600 * hour + 60 * minute + second
    TH, TL = struct.pack('>H', total_seconds)
    TSS = subsecond
    return cls(bytes((DATE1, DATE0, TH, TL, TSS)))


  @classmethod
  def from_datetime(cls,
      T: datetime.datetime = None
      ) -> 'cls':
    """
    Creates an instance from an optional datetime.datetime
    (default PC time) object.

    More info: PCPROG5 (pp. 11)
    """
    if T is None:
      T = datetime.datetime.now()
    pm, hour = divmod(T.hour, 12)
    subsecond = round(T.microsecond * 256 / 1000000)
    return cls.from_params(*cls._normalize_params(
        T.year, T.month, T.day,
        pm, hour, T.minute, T.second, subsecond))

    ## TODO...

  def __init__(self, *args):
    warnings.warn('untested: {}'.format(self.__class__))
    super().__init__()


class SevenBytesPunchTime(BasePunchTime):
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
