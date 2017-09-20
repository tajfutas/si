import struct as _struct


CRC_BITF = 0x8000
CRC_POLY = 0x8005


def crc(data, *, crc_bitf=None, crc_poly=None):
  # References:
  # PCPROG5 (p. 5)
  # Helper.cs 0917311 (#L681-L742)
  crc_bitf = (CRC_BITF if crc_bitf is None else crc_bitf)
  crc_poly = (CRC_POLY if crc_poly is None else crc_poly)
  if len(data) < 2:
    num = 0
  else:
    num = 256 * data[0] + data[1]
    if len(data) > 2:
      i = 3
      while i <= len(data) + 2:
        if i < len(data):
          num2 = 256 * data[i - 1] + data[i]
          i += 1
        else:
          if i == len(data):
            num2 = 256 * data[i - 1]
          else:
            num2 = 0
          i += 2
        for j in range(0, 16):
          test = num & crc_bitf
          num = num + num & 65535
          if num2 & crc_bitf:
            num = num + 1 & 65535
          if test:
            num = (num ^ crc_poly) & 65535
          num2 += num2 & 65535
        i += 1
  return cls(_struct.pack('>H', num))
#keep _struct
