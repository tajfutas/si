import datetime
from enum import Enum
import struct
import typing


class PunchTime:
  pass


class FourBytesPunchTime(PunchTime):

  def __init__(self):
    self._mem = memoryview(bytearray(4))

  @property
  def data(self):
      return self._mem.tobytes()

  @property
  def pm(self):
      return self.tl & 0b00000001

  @property
  def td(self):
      return self._mem[0:1].tobytes()

  @property
  def th(self):
      return self._mem[1:2].tobytes()

  @property
  def tl(self):
      return self._mem[2:3].tobytes()

  @property
  def tss(self):
      return self._mem[3:4].tobytes()

  @property
  def week(self):
      return (self.tl & 0b00110000) >> 4

  @property
  def weekday(self):
      return (self.tl & 0b00001110) >> 1



def from_sitime4(
    b4b: bytes,
    refD: typing.Union[datetime.date, datetime.datetime] = None
    ) -> datetime.datetime:
  assert len(b4b) == 4
  TD = b4b[0:1]
  TH = b4b[1:2]
  TL = b4b[2:3]
  TSS = b4b[3:4]
  rel_week = (TD[0] & 0b00110000) >> 4
  weekday = (TD[0] & 0b00001110) >> 1
  pm = TD[0] & 0b00000001
  total_seconds = struct.unpack('>H', TH + TL)[0]
  hours = total_seconds // 3600
  minutes = total_seconds % 3600 // 60
  seconds = total_seconds % 60
  microseconds = round(TSS[0] * 1000000 / 256)
  if refD is None:
    now = datetime.datetime.now()
    refD = datetime.date(now.year, now.month, now.day)
  ref_weekday = refD.isoweekday() % 7
  if ref_weekday < weekday:
    ref_weekday += 7
  refT = datetime.datetime(refD.year, refD.month, refD.day)
  days_delta = 7 * rel_week + ref_weekday - weekday
  T = refT - datetime.timedelta(days=days_delta)
  T += datetime.timedelta(
    hours = 12 * pm + hours,
    minutes = minutes,
    seconds = seconds,
    microseconds = microseconds)
  return T


def from_sitime63(b6b: bytes) -> datetime.datetime:
  assert len(b6b) == 6
  return from_sitime74(b6b + b'\x00')


def from_sitime74(b7b: bytes) -> datetime.datetime:
  assert len(b7b) == 7
  YY, MM, DD, TWD, THTL, TSS = struct.unpack('>BBBBHB', b7b)
  pm = TWD & 1
  hour = 12 * pm + THTL // 3600
  second = THTL % 3600
  minute = second // 60
  second %= 60
  microsecond = round(TSS * 1000000 / 256)
  return datetime.datetime(_get_YYYY(YY), MM, DD, hour, minute,
      second, microsecond)


def get_card_family(siid: typing.Union[str, int]) -> CardFamily:
  # SPORTident.Common.Helper.GetCardFamilyFromSiid(String)
  try:
    siid = int(siid)
  except ValueError:
    return CardFamily(0)
  if (1000000 <= siid <= 1999999):
    return CardFamily.Card9
  elif (2000000 <= siid <= 2999999):
    return CardFamily.Card8
  elif (4000000 <= siid <= 4999999):
    return CardFamily.PCard
  elif (6000000 <= siid <= 6999999):
    return CardFamily.TCard
  elif (7000000 <= siid <= 9999999):
    return CardFamily(15)
  # TODO: 14
  else:
    return CardFamily(0)


def to_siid(bxb: bytes) -> str:
  # SPORTident.Common.Helper.GetSiidFromBytes(Byte())
  assert (3 <= len(bxb) <= 4)
  b3b = bxb[-3:]  # I want the last three bytes
  if b3b[0] == 1:
    return str(struct.unpack('>H', b3b[1:3])[0])
  elif b3b[0:1] in (b'R', b'U'):
    return '{}{:0>5}'.format(b3b[0:1].decode(),
        struct.unpack('>H', b3b[1:3])[0])
  elif 7 <= b3b[0]:
    return str(struct.unpack('>I', b'\x00' + b3b)[0])
  else:
    upper_value = 100000 * b3b[0]
    lower_value = struct.unpack('>H', b3b[1:3])[0]
    return str(upper_value + lower_value)


def to_sitime4(
    T: datetime.datetime = None,
    refD: typing.Union[datetime.date, datetime.datetime] = None
    ) -> bytes:
  if T is None or refD is None:
    now = datetime.datetime.now()
  if T is None:
    T = now
  if refD is None:
    refT = datetime.datetime(now.year, now.month, now.day)
  else:
    refT = datetime.datetime(refD.year, refD.month, refD.day)
  rel_week = (T - refT).days // 7
  assert (0 <= rel_week < 4)
  weekday = T.isoweekday() % 7
  pm = (T.strftime('%p') == 'PM')
  TD = (rel_week << 4) + (weekday << 1) + pm
  THTLval = (T.hour % 12) * 3600 + T.minute * 60 + T.second
  THTLbyt = THTLval.to_bytes(2, 'big')
  TH = THTLbyt[0]
  TL = THTLbyt[1]
  TSS = round(T.microsecond * 256 / 1000000)
  return bytes((TD, TH, TL, TSS))


def to_sitime63(T: datetime.datetime) -> bytes:
  return to_sitime74(T)[:-1]


def to_sitime74(T: datetime.datetime) -> bytes:
  YY = T.year % 100
  MM = T.month
  DD = T.day
  TWD = ((T.isoweekday() % 7) << 1) + T.hour // 12
  THTLval = (T.hour % 12) * 3600 + T.minute * 60 + T.second
  THTLbyt = THTLval.to_bytes(2, 'big')
  TH = THTLbyt[0]
  TL = THTLbyt[1]
  TSS = round(T.microsecond * 256 / 1000000)
  return bytes((YY, MM, DD, TWD, TH, TL, TSS))
