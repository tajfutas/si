import datetime
from enum import Enum
import struct


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


class CardType(Enum):
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


def from_sidate(bb):
  YY, MM, DD = struct.unpack('BBB', bb)
  return datetime.date(_get_YYYY(YY), MM, DD)


def from_sitime63(bb):
  return from_sitime74(bb + b'\x00')


def from_sitime74(bb):
  YY, MM, DD, TWD, THTL, TSS = struct.unpack('>BBBBHB', bb)
  pm = TWD & 1
  hour = 12 * pm + THTL // 3600
  second = THTL % 3600
  minute = second // 60
  second %= 60
  microsecond = round(TSS * 1000000 / 256)
  return datetime.datetime(_get_YYYY(YY), MM, DD, hour, minute,
      second, microsecond)


def to_sidate(D):
  return bytes((D.year % 100, D.month, D.day))


def to_sitime4(T, rel_week=0):
  assert (0 <= rel_week < 4)
  weekday = T.isoweekday() - 1
  pm = (T.strftime('%p') == 'PM')
  TD = (rel_week << 4) + (weekday << 1) + pm
  THTLval = (T.hour % 12) * 3600 + T.minute * 60 + T.second
  THTLbyt = THTLval.to_bytes(2, 'big')
  TH = THTLbyt[0]
  TL = THTLbyt[1]
  TSS = round(T.microsecond * 256 / 1000000)
  return bytes((TD, TH, TL, TSS))


def to_sitime63(T):
  return to_sitime74(T)[:-1]


def to_sitime74(T):
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
