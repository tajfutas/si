import datetime
from enum import Enum
import struct

from . import common
from . import proto
from . import station

CRC_POLY = 0x8005
CRC_BITF = 0x8000


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
  return struct.pack('>H', num)


class Record(proto.Record):

  class State(Enum):
    NULL = None
    AWAKE = b'\xFF'
    STX = b'\x02'
    CMD = 'cmd'
    LEN = 'len'
    DATA = 'data'
    CRC = 'crc'
    ETX = b'\x03'

  @classmethod
  def from_cmd_and_data(cls, cmd, data=b'', wakeup=True,
      n_stx=2):
    assert (0 < n_stx < 3)
    length_byte = struct.pack('B', len(data))
    base = cmd.value + length_byte + data
    data = (
        (proto.Char.WAKEUP.value if wakeup else b'')
        +
        (n_stx * proto.Char.STX.value)
        +
        base
        +
        get_crc(base)
        +
        proto.Char.ETX.value
        )
    return cls(data)

  def __init__(self, data=None):
    self.state =  self.State['NULL']
    self.raw_data = bytearray()
    self.cmd = None
    self.cmd_i = None
    if data:
      self.send(data)

  @property
  def complete(self):
    return (self.state == self.State['ETX'])

  def data_len_i(self):
    if self.cmd_i:
      data_len_i = self.cmd_i + 1
      if data_len_i < len(self.raw_data):
        return data_len_i

  def data_len(self):
    data_len_i = self.data_len_i()
    if data_len_i:
      return self.raw_data[data_len_i]

  def data_i(self):
    data_len_i = self.data_len_i()
    if data_len_i:
      return data_len_i + 1

  def data(self):
    data_i = self.data_i()
    if data_i:
      data_len = self.data_len()
      data = self.raw_data[data_i:data_i + data_len]
      if len(data) == data_len:
        return data

  def crc_i(self):
    data_i = self.data_i()
    if data_i:
      data_len = self.data_len()
      return data_i + data_len

  def crc(self):
    crc_i = self.crc_i()
    if crc_i:
      crc = self.raw_data[crc_i:crc_i + 2]
      if len(crc) == 2:
        return crc

  def send_when_null(self, data):
    b = data[:1]
    if b == proto.Char['WAKEUP'].value:
      self.state = self.State['AWAKE']
    elif b == proto.Char['STX'].value:
      self.state = self.State['STX']
    else:
      raise ValueError(('invalid extended protocol byte '
          'received at NULL state: {:X}').format(b[0]))
    self.raw_data.extend(b)
    return self.send(data[1:])

  def send_when_awake(self, data):
    b = data[:1]
    if b == proto.Char['STX'].value:
      self.state = self.State['STX']
    elif b != proto.Char['WAKEUP'].value:
      raise ValueError(('invalid extended protocol byte '
          'received at AWAKE state: {:X}').format(b[0]))
    self.raw_data.extend(b)
    return self.send(data[1:])

  def send_when_stx(self, data):
    b = data[:1]
    if b != proto.Char['STX'].value:
      try:
        self.cmd = Cmd(b)
      except ValueError:
        raise ValueError(('invalid extended protocol byte '
            'received at STX state: {:X}').format(b[0]))
      self.cmd_i = len(self.raw_data)
      self.state = self.State['CMD']
    self.raw_data.extend(b)
    return self.send(data[1:])

  def send_when_cmd(self, data):
    self.state = self.State['LEN']
    self.raw_data.extend(data[:1])
    return self.send(data[1:])

  def send_when_len(self, data):
    curr_len = len(self.raw_data[self.data_i():])
    exp_len = self.data_len()
    num_bytes_needed = max(0, exp_len - curr_len)
    num_bytes_available = min(len(data), num_bytes_needed)
    if num_bytes_needed == num_bytes_available:
      self.state = self.State['DATA']
    self.raw_data.extend(data[:num_bytes_available])
    return self.send(data[num_bytes_available:])

  def send_when_data(self, data):
    curr_len = len(self.raw_data[self.crc_i():])
    exp_len = 2
    num_bytes_needed = max(0, exp_len - curr_len)
    num_bytes_available = min(len(data), num_bytes_needed)
    if num_bytes_needed == num_bytes_available:
      self.state = self.State['CRC']
    self.raw_data.extend(data[:num_bytes_available])
    if self.state == self.State['CRC']:
      base = self.raw_data[self.cmd_i:self.crc_i()]
      assert get_crc(base) == self.crc()
    return self.send(data[num_bytes_available:])

  def send_when_crc(self, data):
    b = data[:1]
    if b != proto.Char['ETX'].value:
      raise ValueError(('invalid extended protocol byte '
          'received at CRC state (ETX expected): {:X}').format(
          b[0]))
    self.state = self.State['ETX']
    self.raw_data.extend(b)
    return self.send(data[1:])


class Instruction(proto.Instruction):
  PROTOCOL = 'extended'


class Response(proto.Response):
  PROTOCOL = 'extended'


class GetSystemDataInstruction(Instruction):
  CMD = Cmd.GET_SYS_VAL

  def __init__(self, adr=0, anz=128):
    bb = bytes((adr, anz))
    assert bb[0] + bb[1] <= 128
    self.adr = adr
    self.anz = anz

  @classmethod
  def from_record(cls, r):
    assert r.cmd == cls.CMD
    adr, anz = r.data()
    return cls(adr, anz)

  def record(self, wakeup=True, n_stx=2):
    data = bytes((self.adr, self.anz))
    return Record.from_cmd_and_data(self.CMD, data,
        wakeup=wakeup, n_stx=n_stx)


class GetSystemDataResponse(Response):
  CMD = Cmd.GET_SYS_VAL

  def __init__(self, station_codenr, response_bytes, adr=0):
    self.station_codenr = station_codenr
    self.response_bytes = response_bytes
    anz = len(response_bytes)
    assert adr + anz <= 128
    self.adr = adr

  @classmethod
  def from_record(cls, r):
    assert r.cmd == cls.CMD
    data = r.data()
    station_codenr = station.cn1cn0_to_codenr(data[0:2])
    adr = data[2]
    response_bytes = data[3:]
    return cls(station_codenr, response_bytes, adr)

  def record(self):
    cn1cn0 = station.codenr_to_cn1cn0(self.station_codenr)
    adr_byte = bytes([self.adr])
    data = cn1cn0 + bytes([self.adr]) + self.response_bytes
    return Record.from_cmd_and_data(self.CMD, data,
        wakeup=False, n_stx=1)


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


class Transmit(Response):
  CMD = Cmd.TRANS_REC

  def __init__(self, station_codenr, card_nr, sitime4,
      backup_mem_adr):
    self.station_codenr = station_codenr
    self.card_nr = card_nr
    self.sitime4 = sitime4
    self.backup_mem_adr = backup_mem_adr

  @classmethod
  def from_record(cls, r):
    assert r.cmd == cls.CMD
    data = r.data()
    station_codenr = station.cn1cn0_to_codenr(data[0:2])
    card_nr = struct.unpack('>I', data[2:6])[0]
    sitime4 = data[6:10]
    backup_mem_adr =  data[10:13]
    return cls(station_codenr, card_nr, sitime4,
        backup_mem_adr)

  #def record(self):
  #  cn1cn0 = station.codenr_to_cn1cn0(self.station_codenr)
  #  adr_byte = bytes([self.adr])
  #  data = cn1cn0 + bytes([self.adr]) + self.response_bytes
  #  return Record.from_cmd_and_data(self.CMD, data,
  #      wakeup=False, n_stx=1)
