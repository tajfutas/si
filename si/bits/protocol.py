from enum import Enum


from si.protocol import Protocol as _Protocol

from . import _base
from . import _decorator


class Cmd(Enum):
  "Command codes"
  # References:
  # PCPROG5
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

  02 62 (block: 0x00 to 0x07) (page: 0x00 to 0x07)
  (16 bytes) 03
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
  Read Backup Memory of extended start and extended finish
  only
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


class ProtoChar(Enum):
  "Protocol Characters"
  # References:
  # Communication.cs 9e291aa (#L149-157)
  # PCPROG5 (pp. 5-6)
  # sireader.py 9535938 (#L50-L56)

  # Communication.cs names are prefixed with "C_"
  # ACK is missing from the Communication.cs constants
  STX = b'\x02'
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


@_decorator.enum_defined(Cmd)
class CmdByte(_base.Bytes):
  "Command code byte"
  # References: see Cmd references
  def __init__(self):
    self._protocol = _Protocol(self >= b'\x80'
        and self != b'\xc4')

  @property
  def protocol(self) -> _Protocol:
    "Corresponding si.protocol.Protocol enumeration"
    return self._protocol


@_decorator.enum_defined(ProtoChar)
class ProtoCharByte(_base.Bytes):
  "Protocol character byte"
  # References: see ProtoChar references

del Enum

del _base
del _decorator