from enum import Enum


class ActiveCardCmd(Enum):
  # TODO: more info

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

  # References:
  # Communication.cs 9e291aa (#L27-L31)

  # Communication.cs names are prefixed with "CARD_"
  CARD_COMPLETE = b'\xCC'
  CARD_AUTOSEND = b'\xCA'
  CARD_FAILED = b'\xCF'


del Enum
