import datetime
from enum import Enum
import struct
import typing


# TODO: Review functions and their namespace

def _get_YYYY(YY):
  # standard way:
  #now = datetime.datetime.now()
  #if YY <= now.year - 2000:
  #  year = 2000 + YY
  #else:
  #  year = 1900 + YY
  # my way:
  if YY < 95:
    return 2000 + YY
  else:
    return 1900 + YY


def from_sidate(b3b: bytes) -> datetime.date:
  YY, MM, DD = struct.unpack('BBB', b3b)
  return datetime.date(_get_YYYY(YY), MM, DD)


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
