"""
SPORTident Protocol Format
"""

import struct

from construct import *
from construct.lib import *


# Custom constructs
################################################################

def OptionalConst(bytes_):
  """
  Optional constant field

  Maps to True or False depending on whether the constant is
  parsed or to be builded.

  :param bytes_: the constant bytes
  """
  return ExprAdapter(Range(0, 1, Const(bytes_)),
          decoder = lambda obj,ctx: (
              True if obj == [bytes_] else False),
          encoder = lambda obj,ctx: ([bytes_] if obj else []))


# Main constructs
################################################################

Instruction = 'Instruction' / Struct(
  'ff' / OptionalConst(b'\xFF'),
  'ctrl' / OneOf(Bytes(1), b'\x02\x06\x15'),
  Embedded(
    # https://github.com/construct/construct/issues/296
    IfThenElse(
    this.ctrl == b'\x02',
    Embedded(Struct(
      'extra_stx' / OptionalConst(b'\x02'),
      'cmd' / Bytes(1),
      Embedded(IfThenElse(
        this.cmd >= b'\x80' and this.cmd != b'\xC4',
        Struct(
          'len' / Rebuild(Byte, len_(this.data)),
          Embedded(RawCopy(Bytes(this.len))),
          'crc' / Checksum(Bytes(2), lambda data: crc529(data),
              lambda ctx: (
                  ctx._.cmd
                  + bytes([ctx.len])
                  + ctx.data
              ),
          ),
        ),
        Struct(), # TODO
      )),
      'etx' / Const(b'\x03'),
    )),
    Struct(),
    )
  ),
)


# Helper functions
################################################################

def crc529(bytes_: bytes) -> bytes:
  """
  Create an instance calculated for the given bytes

  Given bytes must include command byte and length byte
  """
  # References:
  # PCPROG5 (p. 5)
  # Helper.cs 9e291aa (#L587-L648)

  CRC_POLY = 0x8005
  CRC_BITF = 0x8000

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
          test = num & CRC_BITF
          num = num + num & 65535
          if num2 & CRC_BITF:
            num = num + 1 & 65535
          if test:
            num = (num ^ CRC_POLY) & 65535
          num2 += num2 & 65535
        i += 1
  # return struct.pack('>H', num) ; return Int16ub.build(num)
  return bytes(divmod(num, 256))




if __name__ == '__main__':
  demo_instr = b'\xff\x02\x02\xE0\x00\xE0\x00\x03'

  #Instruction.parse(b'\xff\x06')
  #Instruction.parse(b'\x15')

  demo_instr = b'\xFF\x02\x02\x83\x83\x08\x46\x00\x0D\x00\x08\x46\x04\x33\x31\x31\x0E\x06\x04\x6F\x21\xFF\xFF\xFF\x02\x06\x00\x1B\x17\x3F\x18\x18\x06\x29\x08\x05\x3E\xFE\x0A\xEB\x0A\xEB\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x92\xBA\x1A\x42\x00\xFF\xFF\xE1\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x0B\x07\x0C\x00\x0D\x5D\x0E\x44\x0F\xEC\x10\x2D\x11\x3B\x12\x73\x13\x23\x14\x3B\x15\x01\x19\x1D\x1A\x1C\x1B\xC7\x1C\x00\x1D\xB0\x21\xB6\x22\x10\x23\xEA\x24\x0A\x25\x00\x26\x11\x2C\x88\x2D\x31\x2E\x0B\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xC4\x28\x03'
  demo_parsed = Instruction.parse(demo_instr)
  d = {k:v for k,v in demo_parsed.items() if k in ('ff', 'ctrl', 'cmd', 'extra_stx', 'data')}
  demo_instr2 = Instruction.build(d)
  demo_parsed2 = Instruction.parse(demo_instr2)

  assert demo_instr == demo_instr2
