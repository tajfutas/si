from enum import IntEnum

__all__ = [
    'bits',
    ]

from . import bits


class ProductFamily(IntEnum):
  # References:
  # SPORTident.Communication 9e291aa \ProductFamily.cs
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


class ProductType(IntEnum):
  # References:
  # SPORTident.Communication 9e291aa \ProductType.cs
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


class SimSrrFrequencyChannels(IntEnum):
  # References:
  # SPORTident.Communication 9e291aa \SimSrrFrequencyChannels.cs
  NotSet = -1
  Red = 0
  Blue = 1
  Yellow = 2
  Green = 3


del IntEnum
