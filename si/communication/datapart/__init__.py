from enum import Enum


class ActiveCardCmd(Enum):
  # TODO: more info
  """
  Active Card Command Codes

  Source Communication.cs 9e291aa (#L117-L125)
  """
  # Communication.cs names are prefixed with "C_ACTIVECARD_"
  BAT_LOW_THRESHOLD = b'\x06'
  ADDR_BATTERY_DATE = b'\x6F'
  ADDR_SEL_FEEDBACK = b'\x73'
  ADDR_BAT_THRESHOLD = b'\x75'
  ADDR_MEASURE_BAT = b'\x7E'


class Card(Enum):
  # TODO: more info
  """
  Card ???

  Source Communication.cs 9e291aa (#L27-L31)
  """
  # Communication.cs names are prefixed with "CARD_"
  CARD_COMPLETE = b'\xCC'
  CARD_AUTOSEND = b'\xCA'
  CARD_FAILED = b'\xCF'


class Cmd(Enum):
  """
  Command Codes

  Source Communication.cs 9e291aa (#L33-L115; #L127-L143)
  """
  # Communication.cs names are prefixed with "C_"
  BEEP_CARD = b'\x06'
  CARD5_DATA_OLD = b'\x31'
  CARD_MOVE_OLD = b'\x46'
  BY2_CARD5_OLD = b'\x49'
  BY2_CARD_OUT_OLD = b'\x4F'
  SERIES_R_CARD5 = b'\x52'
  PUNCH_TRIGGER_OLD = b'\x53'
  TIME_TRIGGER_OLD = b'\x54'
  SERIES_U_CARD5 = b'\x55'
  CARD6_DATA_OLD = b'\x61'
  WRITE_CARD6_PAGE_OLD = b'\x62'
  WRITE_CARD6_WORD_OLD = b'\x64'
  CARD6_IN_OLD = b'\x66'
  SET_MS_OLD = b'\x70'
  GET_MS_OLD = b'\x71'
  SET_SDATA_OLD = b'\x72'
  GET_SDATA_OLD = b'\x73'
  WRITE_BACKUP = b'\x80'
  READ_BACKUP = b'\x81'
  SET_SYSDATA = b'\x82'
  GET_SYSDATA = b'\x83'
  SET_PRINT = b'\x84'
  SET_STDDATA = b'\x86'
  GET_STDDATA = b'\x87'
  SET_SYSDATA2 = b'\x88'
  GET_SYSDATA2 = b'\x89'
  BOOT = b'\x8E'
  RESET = b'\x8F'
  CARD5_DATA = b'\xB1'
  PUNCH_TRIGGER = b'\xD3'
  CLEAR_CARD_VALUE = b'\xE0'
  CARD6_DATA = b'\xE1'
  WRITE_CARD6_PAGE = b'\xE2'
  WRITE_CARD6_WORD = b'\xE4'
  CARD5_IN = b'\xE5'
  CARD6_IN = b'\xE6'
  CARD_OUT = b'\xE7'
  CARD_CARD_X_IN = b'\xE8'
  WRITE_CARDX_WORD = b'\xEA'
  READ_CARDX_WORD = b'\xEB'
  WRITE_CARDX_ID = b'\xEC'
  READ_CARDX_PAGE = b'\xED'
  READ_CARDX_BLOCK = b'\xEF'
  SET_MS = b'\xF0'
  GET_MS = b'\xF1'
  ERASE_B_DATA = b'\xF5'
  SET_TIME = b'\xF6'
  GET_TIME = b'\xF7'
  SET_WPERIOD = b'\xF8'
  BEEP = b'\xF9'
  SET_BAUD = b'\xFE'

class MsMode(Enum):
  """
  MS-Mode

  Sources:
  PCPROG5 (pp. 6, 8)
  Communication.cs 9e291aa (#L145-147)
  """
  # Communication.cs names are prefixed with "C_CFG_MSMODE_"
  MASTER = b'\x4D'
  SLAVE = b'\x53'


class ProtoChar(Enum):
  """
  Protocol Characters

  Sources:
  Communication.cs 9e291aa (#L149-157)
  PCPROG5 (pp. 5-6)
  """
  # Communication.cs names are prefixed with "C_"
  # ACK is missing from the Communication.cs constants
  STX = b'\x02'
  ETX = b'\x03'
  ACK = b'\x06'
  DLE = b'\x10'
  NAK = b'\x15'
  FF = b'\xFF'


class SysAddr(Enum):
  """
  System Addresses

  Sources:
  Communication.cs 9e291aa (#L159-180)
  """
  # Communication.cs names are prefixed with "SYSADR_"
  BN3 = b'\x00'
  BN2 = b'\x01'
  BN1 = b'\x02'
  BN0 = b'\x03'
  CFG2 = b'\x04'
  SV2 = b'\x05'
  SV1 = b'\x06'
  SV0 = b'\x07'
  PROD_YEAR = b'\x08'
  PROD_MONTH = b'\x09'
  PROD_DAY = b'\x0A'
  CFG1 = b'\x0B'
  CFG0 = b'\x0C'
  BMS = b'\x0D'
  X_CAP = b'\x0E'
  X_TIME = b'\x0F'
  ACT = b'\x10'
  STB = b'\x11'
  PUN = b'\x12'
  LUMI = b'\x13'
  FLD = b'\x14'
  BATT_YEAR = b'\x15'
  BATT_MONTH = b'\x16'
  BATT_DAY = b'\x17'
  BATT_CAP3 = b'\x18'
  BATT_CAP2 = b'\x19'
  BATT_CAP1 = b'\x1A'
  BATT_CAP0 = b'\x1B'
  EP3 = b'\x1C'
  EP2 = b'\x1D'
  USB = b'\x1E'
  RS232 = b'\x1F'
  SST = b'\x20'
  EP1 = b'\x21'
  EP0 = b'\x22'
  ACT_M = b'\x23'
  ACT_H = b'\x24'
  ACT_L = b'\x25'
  STB_M = b'\x26'
  STB_H = b'\x27'
  STB_L = b'\x28'
  PUN_M = b'\x29'
  PUN_H = b'\x2A'
  PUN_L = b'\x2B'
  MS = b'\x2C'
  SCA = b'\x2D'
  SICF1 = b'\x2E'
  SICF0 = b'\x2F'
  FCG = b'\x30'
  EWD = b'\x31'
  ESHDN = b'\x32'
  CARD_BLOCKS = b'\x33'
  PI3 = b'\x34'
  PI2 = b'\x35'
  PI1 = b'\x36'
  PI0 = b'\x37'
  PW3 = b'\x38'
  PW2 = b'\x39'
  PW1 = b'\x3A'
  PW0 = b'\x3B'
  PRINT = b'\x3C'
  BCKF = b'\x3D'
  BAUD0 = b'\x3E'
  BAUD1 = b'\x3F'
  AP_FREQ_1 = b'\x30'
  AP_FREQ_2 = b'\x31'
  AP_FREQ_3 = b'\x32'
  AP_FREQ_4 = b'\x33'
  AP_FREQ_C = b'\x34'
  AP_HANDSHAKE = b'\x3E'
  AP_TELEGRAM = b'\x3D'
  AP_PROT = b'\x3F'
  TC1 = b'\x40'
  TC0 = b'\x41'
  TT1 = b'\x42'
  TT0 = b'\x43'
  TO1 = b'\x44'
  TO0 = b'\x45'
  BEEP_LEN1 = b'\x46'
  BEEP_LEN0 = b'\x47'
  PULS_SCAN_ACT1 = b'\x48'
  PULS_SCAN_ACT0 = b'\x49'
  PULS_SCAN_STB1 = b'\x4A'
  PULS_SCAN_STB0 = b'\x4B'
  VBAT_MIN1 = b'\x4C'
  VBAT_MIN0 = b'\x4D'
  BAKE_FIELD = b'\x4E'
  BAKE_DELAY = b'\x4F'
  ADCV_BAT1 = b'\x50'
  ADCV_BAT0 = b'\x51'
  ADCV_BATE1 = b'\x52'
  ADCV_BATE0 = b'\x53'
  FOPT = b'\x58'
  FACU = b'\x59'
  FZYK = b'\x5A'
  MHTS = b'\x5B'
  BOOT_V3 = b'\x60'
  BOOT_V2 = b'\x61'
  BOOT_V1 = b'\x62'
  BOOT_V0 = b'\x63'
  FUNC_MO7 = b'\x64'
  FUNC_MO6 = b'\x65'
  FUNC_MO5 = b'\x66'
  FUNC_MO4 = b'\x67'
  FUNC_MO3 = b'\x68'
  FUNC_MO2 = b'\x69'
  FUNC_MO1 = b'\x6A'
  FUNC_MO0 = b'\x6B'
  STAMP_BUFFER_SIZE = b'\x64'
  STAMP_BUFFER_IN = b'\x66'
  STAMP_BUFFER_OUT_UART = b'\x68'
  STAMP_BUFFER_OUT_GSM = b'\x6A'
  GSM_BDATA = b'\x6D'
  GSM_ASND = b'\x6E'
  GSM_GSMON = b'\x6F'
  SC = b'\x70'
  MO = b'\x71'
  CNL = b'\x72'
  SM_CNH = b'\x73'
  CPC = b'\x74'
  POT_YY = b'\x75'
  POT_MM = b'\x76'
  POT_DD = b'\x77'
  POT_DOW = b'\x78'
  POT_TIMH = b'\x79'
  POT_TIML = b'\x7A'
  TOT_DOW = b'\x7B'
  TOT_TIMH = b'\x7C'
  TOT_TIML = b'\x7D'
  OFF_VALH = b'\x7E'
  OFF_VALL = b'\x7F'
  GSM_SIM_ID_0 = b'\xA0'
  GSM_SIM_ID_1 = b'\xA1'
  GSM_SIM_ID_2 = b'\xA2'
  GSM_SIM_ID_3 = b'\xA3'
  GSM_SIM_PIN = b'\xB0'
  GSM_PROVIDER = b'\xB4'
