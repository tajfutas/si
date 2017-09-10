import enum as _enum

from . import construct as _construct


class ActiveCardCmd(_enum.Enum):
  # TODO: more info

  # References:
  # Communication.cs 9e291aa (#L117-L125)

  # Communication.cs names are prefixed with "C_ACTIVECARD_"
  BAT_LOW_THRESHOLD = b'\x06'
  ADDR_BATTERY_DATE = b'\x6F'
  ADDR_SEL_FEEDBACK = b'\x73'
  ADDR_BAT_THRESHOLD = b'\x75'
  ADDR_MEASURE_BAT = b'\x7E'

activecardcmd = _construct.enum.Enum.factory(ActiveCardCmd, 8)


class Card(_enum.Enum):
  # TODO: more info

  # References:
  # Communication.cs 0917311 (#L87-L91)

  # Communication.cs names are prefixed with "CARD_"
  CARD_COMPLETE = b'\xCC'
  CARD_AUTOSEND = b'\xCA'
  CARD_FAILED = b'\xCF'

card = _construct.enum.Enum.factory(Card, 8)


del _construct
del _enum
