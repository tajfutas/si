import struct as _struct

from si.utils import objbytes


class CrcBytes(objbytes.Bytes):
  "16bit CRC checksum bytes"

  _OCTETS = 0o20

  CRC_POLY = 0x8005
  CRC_BITF = 0x8000

  @classmethod
  def for_bytes(cls, bytes_: bytes) -> 'cls':
    """
    Create an instance calculated for the given bytes

    Given bytes must include command byte and length byte
    """
    # References:
    # PCPROG5 (p. 5)
    # Helper.cs 9e291aa (#L587-L648)
    if len(bytes_) < 2:
      num = 0
    else:
      num = 256 * bytes_[0] + bytes_[1]
      if len(bytes_) > 2:
        i = 3
        while i <= len(bytes_) + 2:
          if i < len(bytes_):
            num2 = 256 * bytes_[i - 1] + bytes_[i]
            i += 1
          else:
            if i == len(bytes_):
              num2 = 256 * bytes_[i - 1]
            else:
              num2 = 0
            i += 2
          for j in range(0, 16):
            test = num & cls.CRC_BITF
            num = num + num & 65535
            if num2 & cls.CRC_BITF:
              num = num + 1 & 65535
            if test:
              num = (num ^ cls.CRC_POLY) & 65535
            num2 += num2 & 65535
          i += 1
    return cls(_struct.pack('>H', num))

  def check_bytes(self, bytes_: bytes) -> bool:
    """
    CRC Check the given bytes with self

    Return True if succeeds and False if fails

    Given bytes must include command byte and length byte
    """
    return (self.__class__.for_bytes(bytes_) == self)


del objbytes
