import enum as _enum_


class ProductFamily(_enum_.IntEnum):
  # References:
  # SPORTident.Communication/ProductFamily.cs 0917311
  NotSet = 0
  SimSrr = 33
  Bs8SiMaster = 136
  Bs10UfoReaderSiGolf = 138
  Bs10UfoReaderSportIdent = 139
  Bsx4 = 148
  Bsx6 = 150
  Bsx7 = 151
  Bsx8 = 152
  Bs11LoopAntenna = 153
  Bs11Large = 154
  Bs11Small = 155
  Bs12GsmUart = 156
  SiGsmDn = 157
  SiPoint = 241


class ProductType(_enum_.IntEnum):
  # References:
  # SPORTident.Communication/ProductType.cs 0917311
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
  Bs11LoopAntenna = 37273
  Bs11Large = 40346
  Bs11Small = 52635
  Bs12GsmUart = 6556
  SiGsmDn = 7069
  SiPointGolf = 37105
  SiPointSportident = 37617


del _enum_
