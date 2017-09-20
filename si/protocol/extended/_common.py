import enum as _enum_


class Cmd(_enum_.Enum):
  "Command codes"
  # References:
  # PCPROG5
  # Communication.cs 9e291aa (#L33-L115; #L127-L143)
  # sireader.py 9535938 (#L59-L111)
  # Clear SI-card by software

  # Communication.cs names are prefixed with "C_"
  # The following commands are known from sireader.py 9535938:
  #   A2  SET_SRR_SYSDATA <- C_SRR_WRITE
  #   A3  GET_SRR_SYSDATA <- C_SRR_READ
  #   A6  SRR_QUERY <- C_SRR_QUERY
  #   A7  SRR_PING <- C_SRR_PING
  #   A8  SRR_ADHOC <- C_SRR_ADHOC
  #   C3  WRITE_CARD5_PAGE <- C_SI5_WRITE

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


del _enum_
