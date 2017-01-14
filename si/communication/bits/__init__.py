from enum import Enum

from . import instruction


__all__ = [
    'instruction',
    ]


class ActiveCardCmd(Enum):
  # TODO: more info
  "Active Card Command Codes"
  # References:
  # Communication.cs 9e291aa (#L117-L125)

  # Communication.cs names are prefixed with "C_ACTIVECARD_"
  BAT_LOW_THRESHOLD = b'\x06'
  ADDR_BATTERY_DATE = b'\x6F'
  ADDR_SEL_FEEDBACK = b'\x73'
  ADDR_BAT_THRESHOLD = b'\x75'
  ADDR_MEASURE_BAT = b'\x7E'


class Card(Enum):
  # TODO: more info
  "Card ???"
  # References:
  # Communication.cs 9e291aa (#L27-L31)

  # Communication.cs names are prefixed with "CARD_"
  CARD_COMPLETE = b'\xCC'
  CARD_AUTOSEND = b'\xCA'
  CARD_FAILED = b'\xCF'


class Cmd(Enum):
  "Command Codes"
  # References:
  # Communication.cs 9e291aa (#L33-L115; #L127-L143)
  # sireader.py 9535938 (#L59-L111)
  # Clear SI-card by software

  # Communication.cs names are prefixed with "C_"
  # The following commands are known from sireader.py 9535938:
  #   30  SET_CARDNO_OLD <- BC_SET_CARDNO
  #   33  PUNCH_TRIGGER_VERYOLD <- BC_TRANS_REC
  #   43  WRITE_CARD5_PAGE_OLD <- BC_SI5_WRITE
  #   63  READ_CARD6_WORD_OLD <- BC_SI6_READWORD
  #   74  READ_BACKUP_OLD <- BC_GET_BACKUP
  #   75  ERASE_B_DATA_OLD <- BC_ERASE_BACKUP
  #   76  SET_TIME_OLD <- BC_SET_TIME
  #   77  GET_TIME_OLD <- BC_GET_TIME
  #   78  SET_WPERIOD_OLD <- BC_OFF
  #   79  RESET_OLD <- BC_RESET
  #   7A  READ_EXTBACKUP_OLD <- BC_GET_BACKUP2
  #   7E  SET_BAUD_OLD <- BC_SET_BAUD
  #   A2  SET_SRR_SYSDATA <- C_SRR_WRITE
  #   A3  GET_SRR_SYSDATA <- C_SRR_READ
  #   A6  SRR_QUERY <- C_SRR_QUERY
  #   A7  SRR_PING <- C_SRR_PING
  #   A8  SRR_ADHOC <- C_SRR_ADHOC
  #   C3  WRITE_CARD5_PAGE <- C_SI5_WRITE
  BEEP_CARD = b'\x06'
  # TODO: more info
  SET_CARDNO_OLD = b'\x30'
  CARD5_DATA_OLD = b'\x31'
  "Read out SI-card 5 data"
  PUNCH_TRIGGER_VERYOLD = b'\x33'
  """
  Autosend timestamp (online control) in very old stations
  (BSF3)
  """
  WRITE_CARD5_PAGE_OLD = b'\x43'
  """
  Write SI-card 5 data page

  02 43 (page: 0x30 to 0x37) (16 bytes) 03
  """
  CARD_MOVE_OLD = b'\x46'
  "SI-card 5 inserted (46 49) or removed (46 4F)"
  BY2_CARD5_OLD = b'\x49'
  BY2_CARD_OUT_OLD = b'\x4F'
  SERIES_R_CARD5 = b'\x52'
  PUNCH_TRIGGER_OLD = b'\x53'
  "Autosend timestamp (online control)"
  TIME_TRIGGER_OLD = b'\x54'
  "Autosend timestamp (lightbeam trigger)"
  SERIES_U_CARD5 = b'\x55'
  CARD6_DATA_OLD = b'\x61'
  """
  Read out SI-card 6 data

  And in compatibility mode:
  Model SI-card 8/9/10/11/SIAC/pCard/tCard as SI-card 6
  """
  WRITE_CARD6_PAGE_OLD = b'\x62'
  """
  Write SI-card 6 data page

  02 62 (block: 0x00 to 0x07) (page: 0x00 to 0x07) (16 bytes) 03
  """
  READ_CARD6_WORD_OLD = b'\x63'
  """
  Read SI-card 6 data word

  02 63 (block: 0x00 to 0x07) (page: 0x00 to 0x07)
    (word: 0x00 to 0x03) 03
  """
  WRITE_CARD6_WORD_OLD = b'\x64'
  """
  Write SI-card 6 data word

  02 64 (block: 0x00 to 0x07) (page: 0x00 to 0x07)
    (word: 0x00 to 0x03) (4 bytes) 03
  """
  CARD6_IN_OLD = b'\x66'
  SET_MS_OLD = b'\x70'
  """
  Set MS-Mode

  53  Slave
  4D  Master
  """
  GET_MS_OLD = b'\x71'
  SET_SDATA_OLD = b'\x72'
  GET_SDATA_OLD = b'\x73'
  READ_BACKUP_OLD = b'\x74'
  # Note: response carries b'\xC4'!
  ERASE_B_DATA_OLD = b'\x75'
  SET_TIME_OLD = b'\x76'
  GET_TIME_OLD = b'\x77'
  SET_WPERIOD_OLD = b'\x78'
  RESET_OLD = b'\x79'
  READ_EXTBACKUP_OLD = b'\x7A'
  """
  Read Backup Memory of extended start and extended finish only
  """
  # Note: response carries b'\xCA'!
  SET_BAUD_OLD = b'\x7E'
  """
  Set station baud rate

  00  4800 baud
  01  38400 baud
  """

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
  SET_SRR_SYSDATA  = b'\xA2'
  "ShortRangeRadio - SysData write"
  GET_SRR_SYSDATA  = b'\xA3'
  "ShortRangeRadio - SysData read"
  SRR_QUERY      = b'\xA6'
  "ShortRangeRadio - network device query"
  SRR_PING       = b'\xA7'
  """
  ShortRangeRadio - ping

  Heartbeat from linked devices, every 50 seconds
  """
  SRR_ADHOC      = b'\xA8'
  "ShortRangeRadio - ad-hoc message i.e. from SI-ActiveCard"
  CARD5_DATA = b'\xB1'
  "Read out SI-card 5 data"
  WRITE_CARD5_PAGE = b'\xC3'
  """
  Write SI-card 5 data page

  02 C3 11 (page: 0x00 to 0x07) (16 bytes) (CRC) 03
  """
  PUNCH_TRIGGER = b'\xD3'
  "autosend timestamp (online control)"
  CLEAR_CARD_VALUE = b'\xE0'
  """
  Clear Card

  Command: 02 E0 00 E0 00 03
  Response: 02 E0 02 (CN) (CRC) 03
  """
  CARD6_DATA = b'\xE1'
  "Read out SI-card 6 data block"
  WRITE_CARD6_PAGE = b'\xE2'
  WRITE_CARD6_WORD = b'\xE4'
  CARD5_IN = b'\xE5'
  "SI-card 5 inserted"
  CARD6_IN = b'\xE6'
  "SI-card 6 inserted"
  CARD_OUT = b'\xE7'
  "SI-card removed"
  CARD_CARD_X_IN = b'\xE8'
  "SI-card 8/9/10/11/p/t inserted"
  WRITE_CARDX_WORD = b'\xEA'
  "Write SI-card 8/9/10/11/p/t data page (double-word)"
  READ_CARDX_WORD = b'\xEB'
  WRITE_CARDX_ID = b'\xEC'
  READ_CARDX_PAGE = b'\xED'
  READ_CARDX_BLOCK = b'\xEF'
  "Read out SI-card 8/9/10/11/p/t data block"
  SET_MS = b'\xF0'
  """
  Set MS-Mode

  53  Slave
  4D  Master
  """
  GET_MS = b'\xF1'
  ERASE_B_DATA = b'\xF5'
  SET_TIME = b'\xF6'
  GET_TIME = b'\xF7'
  SET_WPERIOD = b'\xF8'
  BEEP = b'\xF9'
  """
  Beeps the station N times

  02 F9 01 (number of beeps) (CRC16) 03
  """
  SET_BAUD = b'\xFE'
  """
  Set station baud rate

  00  4800 baud
  01  38400 baud
  """


class MsMode(Enum):
  "MS-Mode"
  # References:
  # PCPROG5 (pp. 6, 8)
  # Communication.cs 9e291aa (#L145-147)

  # Communication.cs names are prefixed with "C_CFG_MSMODE_"
  MASTER = b'\x4D'
  SLAVE = b'\x53'


class ProtoChar(Enum):
  "Protocol Characters"
  # References:
  # Communication.cs 9e291aa (#L149-157)
  # PCPROG5 (pp. 5-6)
  # sireader.py 9535938 (#L50-L56)

  # Communication.cs names are prefixed with "C_"
  # ACK is missing from the Communication.cs constants
  STX = b'\x02',
  """
  Start of text, first byte to be transmitted

  To enable STX detection by the SPORTident station under all
  circumstances two STX-signs should be transmitted at the
  beginning of each record.

  More info:
  PCPROG5 (p. 6)
  """
  ETX = b'\x03'
  "End of text, last byte to be transmitted"
  ACK = b'\x06'
  """
  Positive handshake return

  When sent to BSx3..6 with a card inserted, causes beep
  until SI-card taken out.
  """
  DLE = b'\x10'
  """
  Legacy protool DeLimiter to be inserted before data
  characters 00-1F
  """
  NAK = b'\x15'
  "Negative handshake return"
  FF = b'\xFF'
  """
  Wakeup-byte

  To avoid any data losses this byte should be sent first.

  More info:
  PCPROG5 (p. 6)
  """

class SysAddr(Enum):
  "System Addresses"
  # References:
  # Communication.cs 9e291aa (#L159-180)

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
