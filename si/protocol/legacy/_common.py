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


del _enum_
