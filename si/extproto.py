import collections
import datetime
from enum import Enum
import struct

from . import common
from .legproto import Char

CRC_POLY = 0x8005
CRC_BITF = 0x8000

instruction_part_names = ('wakeup', 'first_stx', 'second_stx',
    'cmd_byte', 'length_byte', 'data', 'crc_16bit', 'etx')
instruction_parts = collections.namedtuple('instruction_parts',
    instruction_part_names)


class Cmd(Enum):
  GET_BACKUP = b'\x81'
  SET_SYS_VAL = b'\x82'
  GET_SYS_VAL = b'\x83'
  SRR_WRITE = b'\xA2'
      # ShortRangeRadio - SysData write
  SRR_READ = b'\xA3'
      # ShortRangeRadio - SysData read
  SRR_QUERY = b'\xA6'
      # ShortRangeRadio - network device query
  SRR_PING = b'\xA7'
      # ShortRangeRadio - heartbeat from linked devices, every
      # 50 seconds
  SRR_ADHOC = b'\xA8'
      # ShortRangeRadio - ad-hoc message, f.ex. from
      # SI-ActiveCard
  GET_SI5 = b'\xB1'
      # read out SI-card 5 data
  SI5_WRITE = b'\xC3'
      # write SI-card 5 data page: 02 C3 11 (page: 0x00 to 0x07)
      # (16 bytes) (CRC) 03
  TRANS_REC = b'\xD3'
      # autosend timestamp (online control)
  CLEAR_CARD = b'\xE0'
      # found on SI-dev-forum: 02 E0 00 E0 00 03
      # (http://www.sportident.com/index.php?option=com_kunena&
      #   view=topic&catid=8&id=56#59)
  GET_SI6 = b'\xE1'
      # read out SI-card 6 data block
  SI5_DET = b'\xE5'
      # SI-card 5 inserted
  SI6_DET = b'\xE6'
      # SI-card 6 inserted
  SI_REM = b'\xE7'
      # SI-card removed
  SI9_DET = b'\xE8'
      # SI-card 8/9/10/11/p/t inserted
  SI9_WRITE = b'\xEa'
      # write data page (double-word)
  GET_SI9 = b'\xEf'
      # read out SI-card 8/9/10/11/p/t data block
  SET_MS = b'\xF0'
  GET_MS = b'\xF1'
  ERASE_BACKUP = b'\xF5'
  SET_TIME = b'\xF6'
  GET_TIME = b'\xF7'
  OFF = b'\xF8'
  BEEP = b'\xF9'
      # 02 F9 01 (number of beeps) (CRC16) 03
  SET_BAUD = b'\xFe'
      # \x00=4800 baud, \x01=38400 baud


valid_cmd_bytes = frozenset(x.value
    for x in Cmd.__members__.values())


def get_crc(bytes_):
  if len(bytes_) < 2:
    return 0
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
  return num


def instr(cmd, data=b''):
  length_byte = struct.pack('B', len(data))
  base = cmd.value + length_byte + data
  crc = struct.pack('>H', get_crc(base))
  return Char.STX.value + base + crc + Char.ETX.value


def split_instr(instr):
  STRUCTURE = (
    (Char.WAKEUP, True),
    (Char.STX, False),
    (Char.STX, True),
    (Cmd, False),
    ('length_byte', False),
    ('data', False),
    ('crc_16bit', False),
    (Char.ETX, False),
    )
  result = [bytearray() for s in STRUCTURE]
  i, si, L, len_data = 0, 0, len(instr), 0
  while i < L:
    byte = bytes([instr[i]])
    for si_ in range(si, len(STRUCTURE)):
      s = STRUCTURE[si_]
      at, optional = s
      if at in Char.__members__.values():
        if byte == at.value:
          result[si_].extend(byte)
          si += 1
          i += 1
          break
        elif optional:
          si += 1
          continue
        else:
          raise ValueError('invalid instruction')
      elif at == Cmd:
        if byte not in valid_cmd_bytes:
          raise ValueError('invalid instruction')
        result[si_].extend(byte)
        si += 1
        i += 1
        break
      elif at == 'length_byte':
        len_data = struct.unpack('B', byte)[0]
        result[si_].extend(byte)
        si += 1
        if len_data == 0:
          si += 1
        i += 1
        break
      elif at == 'data':
        result[si_].extend(byte)
        i += 1
        if len(result[si_]) == len_data:
          si += 1
        break
      elif at == 'crc_16bit':
        result[si_].extend(byte)
        i += 1
        if len(result[si_]) == 2:
          si += 1
        break
      else:
        raise ValueError('invalid instruction')
    else:
      raise ValueError('invalid instruction')
  return instruction_parts(*(bytes(p) for p in result))


class Instruction:

  @classmethod
  def precv(cls):
    pass

  @classmethod
  def psend(cls):
    return instr(self.CMD)

  @classmethod
  def srecv(cls):
    pass

  @classmethod
  def ssend(cls):
    pass

class GetSystemData(Instruction):
  CMD = Cmd.GET_SYS_VAL

  @classmethod
  def precv(cls, sinstr, station):
    if isinstance(sinstr, instruction_parts):
      parts = sinstr
    else:
      parts = split_instr(sinstr)
    assert parts.cmd_byte == cls.CMD.value
    adr = parts.data[2]
    anz = len(parts.data) - 3
    station.mem[adr : adr + anz] = parts.data[3:]

  @classmethod
  def psend(cls, adr=0, anz=128):
    bb = bytes((adr, anz))
    assert bb[0] + bb[1] <= 128
    return instr(cls.CMD, bb)

  @classmethod
  def srecv(cls, pinstr, station):
    if isinstance(pinstr, instruction_parts):
      parts = pinstr
    else:
      parts = split_instr(pinstr)
    assert parts.cmd_byte == cls.CMD.value
    assert len(parts.data) == 2
    adr, anz = parts.data
    assert adr + anz <= 128
    mem = station.mem[adr : adr + anz].tobytes()
    cn10 = station.code_number_cn10
    adr_byte = bytes([adr])
    return instr(cls.CMD, cn10 + adr_byte + mem)


class SetMsMode(Instruction):
  CMD = Cmd.SET_MS

  @classmethod
  def precv(cls, sinstr, station):
    if isinstance(sinstr, instruction_parts):
      parts = sinstr
    else:
      parts = split_instr(sinstr)
    assert parts.cmd_byte == cls.CMD.value
    m_or_s = common.MSMode(parts.data[2])
    station.transfer_mode = m_or_s
    anz = len(parts.data) - 3
    station.mem[adr : adr + anz] = parts.data[3:]

  @classmethod
  def psend(cls, m_or_s=common.MSMode.Master):
    if hasattr(m_or_s, 'value'):
      m_or_s = m_or_s.value
    m_or_s = bytes([m_or_s])
    assert m_or_s[0] in common.MSMode.__members__.values()
    return instr(self.CMD, m_or_s)

  @classmethod
  def srecv(cls, pinstr, station):
    if isinstance(pinstr, instruction_parts):
      parts = pinstr
    else:
      parts = split_instr(pinstr)
    assert parts.cmd_byte == cls.CMD.value
    assert len(parts.data) == 1
    m_or_s = common.MSMode(parts.data[0])
    station.transfer_mode = m_or_s
    cn10 = station.code_number_cn10
    return instr(cls.CMD, cn10 + parts.data)


class GetTime(Instruction):
  CMD = Cmd.GET_TIME

  @classmethod
  def precv(cls, sinstr, station):
    if isinstance(sinstr, instruction_parts):
      parts = sinstr
    else:
      parts = split_instr(sinstr)
    assert parts.cmd_byte == cls.CMD.value
    T = common.from_sitime74(parts.data[2:])
    station.time_diff = T - datetime.datetime.now()

  @classmethod
  def srecv(cls, pinstr, station):
    if isinstance(pinstr, instruction_parts):
      parts = pinstr
    else:
      parts = split_instr(pinstr)
    assert parts.cmd_byte == cls.CMD.value
    assert len(parts.data) == 0
    cn10 = station.code_number_cn10
    T = datetime.datetime.now() + station.time_diff
    data = common.to_sitime74(T)
    return instr(cls.CMD, cn10 + data)


class GetTime(Instruction):
  CMD = Cmd.GET_TIME

  @classmethod
  def precv(cls, sinstr, station):
    if isinstance(sinstr, instruction_parts):
      parts = sinstr
    else:
      parts = split_instr(sinstr)
    assert parts.cmd_byte == cls.CMD.value
    T = common.from_sitime74(parts.data[2:])
    station.time_diff = T - datatime.datetime.now()

  @classmethod
  def srecv(cls, pinstr, station):
    if isinstance(pinstr, instruction_parts):
      parts = pinstr
    else:
      parts = split_instr(pinstr)
    assert parts.cmd_byte == cls.CMD.value
    assert len(parts.data) == 0
    cn10 = station.code_number_cn10
    T = datetime.datetime.now() + station.time_diff
    data = common.to_sitime74(T)
    return instr(cls.CMD, cn10 + data)


class TriggerPunch(Instruction):
  CMD = Cmd.TRANS_REC

  @classmethod
  def ssend(cls, station, bmem_adr):
    assert (station.START_ADR <= bmem_adr < station.MEM_SIZE-8)
    cn10 = station.code_number_cn10
    data = station.mem[bmem_adr:bmem_adr+8].tobytes()
    mem = struct.pack('>I', bmem_adr)[1:]
    return instr(cls.CMD, cn10 + data + mem)
