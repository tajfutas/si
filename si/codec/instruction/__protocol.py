import enum as _enum_


class ProtoChar(_enum_.Enum):
  "Protocol Characters"
  # References:
  # Communication.cs 0917311 (#L225-L233)
  # PCPROG5 (pp. 5-6)
  # sireader.py 9535938 (#L50-L56)

  # Communication.cs names are prefixed with "C_"
  # ACK is missing from the Communication.cs constants

  STX = 0x02
  """
  Start of text, first byte to be transmitted

  To enable STX detection by the SPORTident station under all
  circumstances two STX-signs should be transmitted at the
  beginning of each record.

  More info:
  PCPROG5 (p. 6)
  """

  ETX = 0x03
  "End of text, last byte to be transmitted"

  ACK = 0x06
  """
  Positive handshake return

  When sent to BSx3..6 with a card inserted, causes beep
  until SI-card taken out.
  """

  DLE = 0x10
  """
  Legacy protool DeLimiter to be inserted before data
  characters 00-1F
  """

  NAK = 0x15
  "Negative handshake return"

  WAKEUP = 0xFF
  """
  Wakeup-byte

  To avoid any data losses this byte should be sent first.

  More info:
  PCPROG5 (p. 6)
  """


del _enum_
