import datetime
from enum import Enum
import struct
import typing


class AirPlusRadioMode(Enum):
  NotSetOrDisabled = 0
  SrRadioSendLast = 1
  SrRadioSendAll = 2
  SrRadioSendAllNew = 3


class AirPlusSpecialMode(Enum):
  NotSetOrDisabled = 0
  SiacBatteryTest = 123
  SiacSwitchOn = 124
  SiacSwitchOff = 125
  SiacRadioReadout = 127


class BeaconTimingMode(Enum):
  Unknown = -1
  TimingMode = 0
  PunchingMode = 1


class CardFamily(Enum):
  Card5Card6 = 0
  Card9 = 1
  Card8 = 2
  PCard = 4
  TCard = 6
  FCard = 14
  Card10 = 15
  ActiveCard = 15
  Card11 = 15


class CardType(Enum):
  # SPORTident.CardType
  NotSet = 0
  Card5 = 1
  Card6 = 2
  Card8 = 3
  Card9 = 4
  Card10 = 5
  Card11 = 6
  PCard = 7
  Card_5U = 8
  Card_5R = 9
  TCard = 10
  FCard = 11
  ActiveCard = 12
  ComCardUp = 13
  ComCardPro = 14
  ComCardAir = 15


class DayOfWeek(Enum):
  Sunday = 0
  Monday = 1
  Tuesday = 2
  Wednesday = 3
  Thursday = 4
  Friday = 5
  Saturday = 6
  NotSetOrInvalid = 7


class EvaluationStatus(Enum):
  NotSet = 0
  Pending = 1
  Finished = 2
  Lapped = 3
  DidNotStart = -1
  DidNotFinish = -2
  Disqualified = -3
  NotPlaced = -4
  NotCompetitive = -5


class EventForm(Enum):
  Single = 0
  Relay = 1


class FractionType(Enum):
  None_ = 0
  One50Th = 50
  One256Th = 256


class MSMode(Enum):
  Master = 77
  Slave = 83


class OperatingMode(Enum):
  Unknown = 0
  DControl = 1
  Control = 2
  Start = 3
  Finish = 4
  Readout = 5
  ClearKeepStno = 6
  Clear = 7
  Check = 10
  Printout = 11
  StartWithTime = 12
  FinishWithTime = 13
  BcDControl = 17
  BcControl = 18
  BcStart = 19
  BcFinish = 20
  BcLineMasSta = 28
  BcLineMasFin = 29
  BcLineSlave1 = 30
  BcLineSlave2 = 31


class ProductFamily(Enum):
  _Obsolete = NotImplemented
  NotSet = 0
  SimSrr = 33
  Bs8SiMaster = 136
  Bs10UfoReaderSiGolf = 138
  Bs10UfoReaderSportIdent = 139
  Bsx4 = 148
  Bsx6 = 150
  Bsx7 = 151
  Bsx8 = 152
  Bs11Large = 154
  Bs11Small = 155
  Bs12GsmUart = 156
  SiGsmSrr = 157
  SiPoint = 241


class ProductType(Enum):
  _Obsolete = NotImplemented
  NotSet = 0
  SimSrr = 33
  Bs8SiMaster = 33160
  Bs10UfoReaderSiGolf = 35210
  Bs10UfoReaderSportIdent = 35211
  Bsx4 = 148
  Bsx6 = 150
  Bsf7 = 33175
  Bsm7 = 37271
  Bs7S = 38295
  Bs7P = 45463
  Bsf8 = 33176
  Bsm8 = 37272
  Bs11Large = 40346
  Bs11Small = 52635
  Bs12GsmUart = 6556
  SiGsmSrr = 7069
  SiPointGolf = 37105
  SiPointSportident = 37617


class SimSrrFrequencyChannels(Enum):
  NotSet = -1
  Red = 0
  Blue = 1
  Yellow = 2
  Green = 3


class StampSource(Enum):
  Readout = 0
  Online = 1
  Backup = 2
  RadioReadout = 3


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
