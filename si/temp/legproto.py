from enum import Enum

from . import proto

class Cmd(Enum):
  SET_CARDNO = b'\x30'
  GET_SI5 = b'\x31'
  TRANS_REC = b'\x33'
  SI5_WRITE = b'\x43'
  SI5_DET = b'\x46'
  TRANS_REC2 = b'\x53'
  TRANS_TIME = b'\x54'
  GET_SI6 = b'\x61'
  SI6_WRITEPAGE = b'\x62'
  SI6_READWORD = b'\x63'
  SI6_WRITEWORD = b'\x64'
  SI6_DET = b'\x66'
  SET_MS = b'\x70'
  GET_MS = b'\x71'
  SET_SYS_VAL = b'\x72'
  GET_SYS_VAL = b'\x73'
  GET_BACKUP = b'\x74'
  ERASE_BACKUP = b'\x75'
  SET_TIME = b'\x76'
  GET_TIME = b'\x77'
  OFF = b'\x78'
  RESET = b'\x79'
  GET_BACKUP2 = b'\x7a'
  SET_BAUD = b'\x7e'


def instr(cmd, data):
  return (
      proto.Char.STX.value
      +
      cmd.value
      +
      data
      +
      proto.Char.ETX.value
      )


class LegacyProtocolInstruction(proto.Instruction):
  PROTOCOL = 'legacy'


class GetSystemData(LegacyProtocolInstruction):
  CMD = Cmd.GET_SYS_VAL