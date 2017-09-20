import enum as _enum_


BS11_LOOP_ANTENNA_SN = frozenset((
    # References:
    # SPORTident.Communication/Communication.cs
    #   0917311 (#L10207-L10238)
    301101,
    301102,
    301103,
    301104,
    301105,
    301410,
    301411,
    301568,
    301569,
    301570,
    301571,
    301572,
    301573,
    301734,
    301735,
    301743,
    301744,
    301745,
    301875,
    301876,
    301920,
    302065,
    302066,
    302354,
    302355,
    302356,
    302357,
    302358,
    302359,
  ))


class MsMode(_enum_.Enum):
  "MS-Mode"
  # References:
  # PCPROG5 (pp. 6, 8)
  # Communication.cs 9e291aa (#L145-147)

  # Communication.cs names are prefixed with "C_CFG_MSMODE_"
  Master = b'\x4D'
  Slave = b'\x53'
  Direct = b'\x4D'
  Remote = b'\x53'


class ProductFamily(_enum_.Enum):
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


class ProductType(_enum_.Enum):
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


class SysAddr(_enum_.IntEnum):
  "System addresses"
  # References:
  # Communication.cs 0917311 (#L247-523)

  # Communication.cs names are prefixed with "SYSADR_"
  BN3 = 0x00
  BN2 = 0x01
  BN1 = 0x02
  BN0 = 0x03
  CFG2 = 0x04
  SV2 = 0x05
  SV1 = 0x06
  SV0 = 0x07
  PROD_YEAR = 0x08
  PROD_MONTH = 0x09
  PROD_DAY = 0x0A
  CFG1 = 0x0B
  CFG0 = 0x0C
  BMS = 0x0D
  X_CAP = 0x0E
  X_TIME = 0x0F
  ACT = 0x10
  STB = 0x11
  PUN = 0x12
  LUMI = 0x13
  FLD = 0x14
  BATT_YEAR = 0x15
  BATT_MONTH = 0x16
  BATT_DAY = 0x17
  BATT_CAP3 = 0x18
  BATT_CAP2 = 0x19
  BATT_CAP1 = 0x1A
  BATT_CAP0 = 0x1B
  EP3 = 0x1C
  EP2 = 0x1D
  USB = 0x1E
  RS232 = 0x1F
  SST = 0x20
  EP1 = 0x21
  EP0 = 0x22
  ACT_M = 0x23
  ACT_H = 0x24
  ACT_L = 0x25
  STB_M = 0x26
  STB_H = 0x27
  STB_L = 0x28
  PUN_M = 0x29
  PUN_H = 0x2A
  PUN_L = 0x2B
  MS = 0x2C
  SCA = 0x2D
  SICF1 = 0x2E
  SICF0 = 0x2F
  FCG = 0x30
  EWD = 0x31
  ESHDN = 0x32
  CARD_BLOCKS = 0x33
  PI3 = 0x34
  PI2 = 0x35
  PI1 = 0x36
  PI0 = 0x37
  PW3 = 0x38
  PW2 = 0x39
  PW1 = 0x3A
  PW0 = 0x3B
  PRINT = 0x3C
  BCKF = 0x3D
  BAUD0 = 0x3E
  BAUD1 = 0x3F
  AP_FREQ_1 = 0x30
  AP_FREQ_2 = 0x31
  AP_FREQ_3 = 0x32
  AP_FREQ_4 = 0x33
  AP_FREQ_C = 0x34
  AP_HANDSHAKE = 0x3E
  AP_TELEGRAM = 0x3D
  AP_PROT = 0x3F
  TC1 = 0x40
  TC0 = 0x41
  TT1 = 0x42
  TT0 = 0x43
  TO1 = 0x44
  TO0 = 0x45
  BEEP_LEN1 = 0x46
  BEEP_LEN0 = 0x47
  PULS_SCAN_ACT1 = 0x48
  PULS_SCAN_ACT0 = 0x49
  PULS_SCAN_STB1 = 0x4A
  PULS_SCAN_STB0 = 0x4B
  VBAT_MIN1 = 0x4C
  VBAT_MIN0 = 0x4D
  BAKE_FIELD = 0x4E
  BAKE_DELAY = 0x4F
  ADCV_BAT1 = 0x50
  ADCV_BAT0 = 0x51
  ADCV_BATE1 = 0x52
  ADCV_BATE0 = 0x53
  FOPT = 0x58
  FACU = 0x59
  FZYK = 0x5A
  MHTS = 0x5B
  BOOT_V3 = 0x60
  BOOT_V2 = 0x61
  BOOT_V1 = 0x62
  BOOT_V0 = 0x63
  FUNC_MO7 = 0x64
  FUNC_MO6 = 0x65
  FUNC_MO5 = 0x66
  FUNC_MO4 = 0x67
  FUNC_MO3 = 0x68
  FUNC_MO2 = 0x69
  FUNC_MO1 = 0x6A
  FUNC_MO0 = 0x6B
  STAMP_BUFFER_SIZE = 0x64
  STAMP_BUFFER_IN = 0x66
  STAMP_BUFFER_OUT_UART = 0x68
  STAMP_BUFFER_OUT_GSM = 0x6A
  GSM_BDATA = 0x6D
  GSM_ASND = 0x6E
  GSM_GSMON = 0x6F
  SC = 0x70
  MO = 0x71
  CNL = 0x72
  SM_CNH = 0x73
  CPC = 0x74
  POT_YY = 0x75
  POT_MM = 0x76
  POT_DD = 0x77
  POT_DOW = 0x78
  POT_TIMH = 0x79
  POT_TIML = 0x7A
  TOT_DOW = 0x7B
  TOT_TIMH = 0x7C
  TOT_TIML = 0x7D
  OFF_VALH = 0x7E
  OFF_VALL = 0x7F
  GSM_SIM_ID_0 = 0xA0
  GSM_SIM_ID_1 = 0xA1
  GSM_SIM_ID_2 = 0xA2
  GSM_SIM_ID_3 = 0xA3
  GSM_SIM_PIN = 0xB0
  GSM_PROVIDER = 0xB4

del _enum_
