import datetime
import math
import struct

import si

PF = si.common.ProductFamily
PT = si.common.ProductType


def codenr_to_cn1cn0(codenr):
  return struct.pack('>H', codenr)


def cn1cn0_to_codenr(cn1cn0):
  return struct.unpack('>H',cn1cn0)[0]


class RegisterSIStationTypes(type):
  # http://python-3-patterns-idioms-test.readthedocs.io/en/lates
  # t/Metaprogramming.html#example-self-registration-of-subclass
  # es
    def __init__(cls, name, bases, nmspc):
        super().__init__(name, bases, nmspc)
        if not hasattr(cls, '_children'):
            cls._children = set()
        cls._children.add(cls)
        cls._children -= set(bases) # Remove base classes
    @property
    def children(cls):
      return frozenset(cls._children)


class SIStation(metaclass=RegisterSIStationTypes):

  MEM_SIZE = 0x1FFFF + 1
  START_ADR = 0x100
  SYSDATA_SIZE = 128

  product_family = PF.NotSet
  product_type = PT.NotSet
  product_type_c1_byte = b'\x00'

  attached_srr_module = False
  has_battery = True
  has_realtime_clock = True
  realtime_clock_enabled = True

 # additional_extproto_instructions = frozenset((  # experimental
 #     si.extproto.GetSystemData,
 #     si.extproto.GetTime,
 #     si.extproto.SetMsMode,
 #     ))

  @classmethod
  def product_config(cls):
    return (cls.product_type_c1_byte
        + struct.pack('B', cls.product_family.value))

  @classmethod
  def sysdata_matches(cls, bb):
    if not isinstance(bb, bytes):
      bb = bytes(bb)
    if len(bb) != cls.SYSDATA_SIZE:
      return False
    bb_product_config = bb[11:13]
    if bb_product_config != cls.product_config():
      return False
    return True

  @classmethod
  def from_sysdata(cls, bb):
    if not isinstance(bb, bytes):
      bb = bytes(bb)
    s = [c for c in cls.children if c.sysdata_matches(bb)]
    inst = s[0]()
    inst.mem[:len(bb)] = bb
    return inst

  def __init__(self):
    self._mem = memoryview(bytearray(self.MEM_SIZE))
    self._mem[12] = self.product_family.value
    self.time_diff = datetime.timedelta(0)  # experimental
    self.transfer_mode = si.common.MSMode.Master  # experimental
    self.legacy_protocol_mode = False  # experimental
    self.instr = {i.CMD: i for c in self.__class__.__mro__
        if hasattr(c, 'additional_extproto_instructions')
        for i in c.additional_extproto_instructions
        }  # experimental

  @property
  def mem(self):
    return self._mem

  def sysdata_str(self):
    return '\n'.join(' '.join('{:>02X}'.format(x)
        for x in self.mem[16*c : 16*c + 16])
        for c in range(self.SYSDATA_SIZE // 16))

  @property
  def serial_number(self):
    bb = self.mem[0:4].tobytes()
    return struct.unpack('>I', bb)[0]
  @serial_number.setter
  def serial_number(self, v):
    self.mem[0:4] = struct.pack('>I', v)

  @property
  def bus_type_byte(self):
    return self.mem[4:5].tobytes()
  @bus_type_byte.setter
  def bus_type_byte(self, b):
    self.mem[4:5] = b

  @property
  def firmware_version(self):
    v = self.mem[5:8].tobytes()
    if v != b'\x00\x00\x00':
      return v.decode('ascii')
  @firmware_version.setter
  def firmware_version(self, s):
    self.mem[5:8] = '{:0>3}'.format(s).encode('ascii')
  @property
  def firmware_version_value(self):
    try:
      return int(self.firmware_version)
    except:
      return 0
    return self.mem[5:8].tobytes().decode('ascii')
  @firmware_version_value.setter
  def firmware_version_value(self, v):
    self.firmware_version = str(v)

  @property
  def production_date(self):
    bb = self.mem[8:11].tobytes()
    try:
      return si.common.from_sidate(bb)
    except ValueError:
      pass
  @production_date.setter
  def production_date(self, D):
    self.mem[8:11] = si.common.to_sidate(D)

  def send(self, obj):  # experimental
    pass


class SIControlStationMixin:

  #additional_extproto_instructions = frozenset((  # experimental
  #    si.extproto.TriggerPunch,
  #    ))

  @property
  def board_version(self):
    return self.mem[12] & 0b1111

  @property
  def backup_memory_size(self):
    v = self.mem[13]
    return (0 if v == 255 else v)
  @backup_memory_size.setter
  def backup_memory_size(self, v):
    self.mem[13] = v

  @property
  def battery_date(self):
    bb = self.mem[21:24].tobytes()
    try:
      return si.common.from_sidate(bb)
    except ValueError:
      pass
  @battery_date.setter
  def battery_date(self, D):
    self.mem[21:24] = si.common.to_sidate(D)

  @property
  def battery_capacity(self):
    bb = self.mem[24:28].tobytes()
    v = struct.unpack('>I', bb)[0] / 3600
    return (v if v < 100000 else 0)
  @battery_capacity.setter
  def battery_capacity(self, v):
    self.mem[24:28] = struct.pack('>I', round(v * 3600))

  @property
  def backup_memory_pointer(self):
    v = struct.unpack('>I', self.mem[28:30].tobytes()
        + self.mem[33:35].tobytes())[0]
    v1 = max(v, self.START_ADR)
    if v != v1:
      self.backup_memory_pointer = v1
    return v1
  @backup_memory_pointer.setter
  def backup_memory_pointer(self, v):
    # TODO
    bmem_full, v1 = divmod(v, self.MEM_SIZE)
    v2 = max(v1, self.START_ADR)
    bb = struct.pack('>I', v2)
    self.mem[28:30] = bb[:2]
    self.mem[33:35] = bb[2:]
  @backup_memory_pointer.deleter
  def backup_memory_pointer(self):
    self.backup_memory_pointer = self.START_ADR

  @property
  def ewd_counter(self):
    return self.mem[49]
  @ewd_counter.setter
  def ewd_counter(self, v):
    self.mem[49] = v

  @property
  def card6_with_112_records(self):
    return (self.mem[51] == 255)
  @card6_with_112_records.setter
  def card6_with_112_records(self, bo):
    self.mem[51] = (255 if bo else 0)

  @property
  def battery_capacity_consumed(self):
    if self.mem[52] == 255:
      return -1.0
    else:
      bb = self.mem[52:56].tobytes()
      return struct.unpack('>I', bb)[0] / 3600
  @battery_capacity_consumed.setter
  def battery_capacity_consumed(self, v):
    bb = struct.pack('>I', round(v * 3600))
    self.mem[52:56] = bb

  @property
  def backup_memory_full(self):
    return self.mem[61] & 0b1111111
  @backup_memory_full.setter
  def backup_memory_full(self, v):
    assert (0 <= v <= 127)
    self.mem[61] = (self.mem[61] & 0b10000000) + v

  @property
  def eco_mode(self):
    return (self.mem[78] == 1 and self.mem[79] == 5)
  @eco_mode.setter
  def eco_mode(self, bo):
    if bo:
      self.mem[78:80] = b'\x01\x05'
    else:
      self.mem[78:80] = b'\x00\x00'

  @property
  def battery_voltage(self):
    bb = self.mem[80:82].tobytes()
    v = struct.unpack('>H', bb)[0]
    if v > 13100:
      v /= 131
    return math.floor(v) / 100
  @battery_voltage.setter
  def battery_voltage(self, v):
    v *= 100
    v *= 131
    self.mem[80:82] = struct.pack('>H', math.floor(v))

  @property
  def battery_temperature(self):
    bb = self.mem[82:84].tobytes()
    v = struct.unpack('>H', bb)[0]
    if v >= 25800:
      return (v - 25800) / 92
    else:
      return v / 10
  @battery_temperature.setter
  def battery_temperature(self, v):
    v = round(v * 92) + 25800
    self.mem[82:84] = struct.pack('>H', math.floor(v))

  @property
  def boot_version(self):
    v = self.mem[96:100].tobytes()
    if v != b'\x00\x00\x00\x00':
      return v.decode('ascii')
  @boot_version.setter
  def boot_version(self, s):
    self.mem[96:100] = '{:0>4}'.format(s).encode('ascii')

  @property
  def allowed_function_modes(self):
    return self.mem[100:108].tobytes()
  @allowed_function_modes.setter
  def allowed_function_modes(self, bb):
    self.mem[100:108] = bb

  @property
  def allow_gate_mode(self):
    if (10 <= self.board_version
        and 332 <= self.firmware_version_value):
      return (self.mem[112] & 0b10000 == 0b10000)
    else:
      return False
  @allow_gate_mode.setter
  def allow_gate_mode(self, bo):
    if self.board_version < 10:
      errmsg = 'board version is lower than 10'
      raise TypeError(errmsg)
    elif self.firmware_version_value <  332:
      errmsg = 'firmware version lower than 332'
      raise TypeError(errmsg)
    v = bool(bo) * 0b10000
    self.mem[112] = (self.mem[112] & 0b11101111) + v

  @property
  def acoustic_signal(self):
    return (self.mem[115] & 0b100 == 0b100)
  @acoustic_signal.setter
  def acoustic_signal(self, bo):
    v = bool(bo) * 0b100
    self.mem[115] = (self.mem[115] & 0b11111011) + v

  @property
  def optical_signal1(self):
    return (self.mem[115] & 0b1 == 0b1)
  @optical_signal1.setter
  def optical_signal1(self, bo):
    v = bool(bo) * 0b1
    self.mem[115] = (self.mem[115] & 0b11111110) + v

  @property
  def optical_signal2(self):
    if (10 <= self.board_version):
      return (self.mem[115] & 0b10 == 0b10)
    else:
      return False
  @optical_signal2.setter
  def optical_signal2(self, bo):
    if self.board_version < 10:
      errmsg = 'board version is lower than 10'
      raise TypeError(errmsg)
    v = bool(bo) * 0b10
    self.mem[115] = (self.mem[115] & 0b11111101) + v

  @property
  def operating_mode(self):
    v = self.mem[113] & 0b11111
    try:
      return si.common.OperatingMode(v)
    except ValueError:
      return si.common.OperatingMode.Unknown
  @operating_mode.setter
  def operating_mode(self, O):
    v = O.value
    assert (0 <= v <= 0b11111)
    self.mem[113] = (self.mem[113] & 0b11100000) + v

  @property
  def srr_mode(self):
    if ((16 < self.operating_mode.value
            and 10 <= self.board_version)
        or (7 <= self.board_version
            and 588 <= self.firmware_version_value)):
      v = self.mem[113] & 0b11000000
      return sr_common.AirPlusRadioMode(v >> 6)
  @srr_mode.setter
  def srr_mode(self, M):
    if 10 <= self.board_version:
      if self.operating_mode.value <= 16:
        errmsg = 'bad operating mode'
        raise TypeError(errmsg)
    elif 7 <= self.board_version:
      if self.firmware_version_value < 588:
        errmsg = 'firmware version lower than 588'
        raise TypeError(errmsg)
    if not isinstance(M, sr_common.AirPlusRadioMode):
      M = sr_common.AirPlusRadioMode(M)
    v = M.value << 6
    self.mem[113] = (self.mem[113] & 0b111111) + v

  @property
  def beacon_mode(self):
    if 10 <= self.board_version:
      return si.common.BeaconTimingMode(self.mem[113] >> 5)
    else:
      return si.common.BeaconTimingMode.Unknown
  @beacon_mode.setter
  def beacon_mode(self, M):
    if self.board_version < 10:
      errmsg = 'board version is lower than 10'
      raise TypeError(errmsg)
    if not isinstance(M, sr_common.BeaconTimingMode):
      assert M in (0, 1)
      M = sr_common.BeaconTimingMode(M)
    v = M.value << 5
    self.mem[113] = (self.mem[113] & 0b11011111) + v

  @property
  def code_number(self):
    if 10 <= self.board_version:
      vh = (self.mem[115] & 0b1000000) << 2
    else:
      vh = (self.mem[115] & 0b11000000) << 2
    return vh + self.mem[114]
  @code_number.setter
  def code_number(self, v):
    if self.board_version < 10:
      maxv = 511
    else:
      maxv = 1023
    assert (0 <= v <= maxv)
    vh, vl = divmod(v, 256)
    vh_ = vh << 6
    self.mem[115] = (self.mem[115] & 0b111111) + vh_
    self.mem[114] = vl

  @property
  def code_number_cn(self):
    return struct.pack('B', self.code_number)

  @property
  def code_number_cn10(self):
    return cn1cn0_from_code_nr(self.code_number)


  @property
  def airplus_special_mode(self):
    dcontrol = si.common.OperatingMode.DControl
    if self.operating_mode == dcontrol:
      code_number = self.code_number
      try:
        return si.common.AirPlusSpecialMode(code_number)
      except ValueError:
        pass
    return si.common.AirPlusSpecialMode.NotSetOrDisabled

  @property
  def legacy_protocol_mode(self):
    b = 0b1
    return (self.mem[116] & b != b)
  @legacy_protocol_mode.setter
  def legacy_protocol_mode(self, bo):
    bc = 0b11111110
    v = (not bool(bo))
    self.mem[116] = (self.mem[116] & bc) + v

  @property
  def auto_send_mode(self):
    b = 0b10
    return (self.mem[116] & b == b)
  @auto_send_mode.setter
  def auto_send_mode(self, bo):
    bc = 0b11111101
    v = bool(bo) << 1
    self.mem[116] = (self.mem[116] & bc) + v

  @property
  def communication_mode(self):
    b = 0b100
    return (self.mem[116] & b == b)
  @communication_mode.setter
  def communication_mode(self, bo):
    bc = 0b11111011
    v = bool(bo) << 2
    self.mem[116] = (self.mem[116] & bc) + v

  @property
  def sprint_mode(self):
    b = 0b1000
    return (self.mem[116] & b == b)
  @sprint_mode.setter
  def sprint_mode(self, bo):
    bc = 0b11110111
    v = bool(bo) << 3
    self.mem[116] = (self.mem[116] & bc) + v

  @property
  def stop_if_backup_full(self):
    b = 0b100000
    return (self.mem[116] & b == b)
  @stop_if_backup_full.setter
  def stop_if_backup_full(self, bo):
    bc = 0b11011111
    v = bool(bo) << 5
    self.mem[116] = (self.mem[116] & bc) + v

  @property
  def last_config_modification(self):
    bb = self.mem[117:123].tobytes()
    try:
      return si.common.from_sitime63(bb)
    except ValueError:
      pass
  @last_config_modification.setter
  def last_config_modification(self, T):
    self.mem[117:123] = si.common.to_sitime63(T)

  @property
  def operating_time(self):
    bb = self.mem[126:128].tobytes()
    v = struct.unpack('>H', bb)[0]
    v = min(max(v, 2), 5759)
    return datetime.timedelta(seconds=v)
  @operating_time.setter
  def operating_time(self, T):
    if hasattr(T, 'total_seconds'):
      T = int(T.total_seconds())
    assert (2 <= T <= 5759)
    self.mem[126:128] = struct.pack('>H', T)


  def trigger_punch(self, card_number, time):
    sn = struct.pack('>I', card_number)
    td, th, tl, tss = si.common.to_sitime4(time)
    adr = self.backup_memory_pointer
    self.mem[adr:adr+8] = sn + td + th + t1 + tss
    self.send((card_number, time, adr))  # experimental


class Bsf7(SIStation,
    SIControlStationMixin):
  product_family = PF.Bsx7
  product_type = PT.Bsf7
  product_type_c1_byte = b'\x81'


class Bsm7(SIStation,
    SIControlStationMixin):
  product_family = PF.Bsx7
  product_type = PT.Bsm7
  product_type_c1_byte = b'\x91'


class Bs7S(SIStation,
    SIControlStationMixin):
  product_family = PF.Bsx7
  product_type = PT.Bs7S
  product_type_c1_byte = b'\x95'


class Bs7P(SIStation,
    SIControlStationMixin):
  product_family = PF.Bsx7
  product_type = PT.Bs7P
  product_type_c1_byte = b'\xB1'


class Bsf8Srr(SIStation,
    SIControlStationMixin):
  product_family = PF.Bsx8
  product_type = PT.Bsf8
  product_type_c1_byte = b'\x91'
  attached_srr_module = True

  @classmethod
  def mem_matches(cls, bb):
    if not isinstance(bb, bytes):
      bb = bytes(bb)
    m0 = super().mem_matches(bb)
    if not m0:
      return m0
    bb_bus_type_byte = bb[4]
    if bb_bus_type_byte & 0b111000 == 0b110000:
      return False
    return True

class Bsm8(SIStation,
    SIControlStationMixin):
  product_family = PF.Bsx8
  product_type = PT.Bsm8
  product_type_c1_byte = b'\x91'
  has_battery = False

  @classmethod
  def mem_matches(cls, bb):
    if not isinstance(bb, bytes):
      bb = bytes(bb)
    m0 = super().mem_matches(bb)
    if not m0:
      return m0
    bb_bus_type_byte = bb[4]
    if bb_bus_type_byte & 0b111000 != 0b110000:
      return False
    return True

class Bsf8(SIStation,
    SIControlStationMixin):
  product_family = PF.Bsx8
  product_type = PT.Bsf8
  product_type_c1_byte = b'\x81'


class Bs8SiMaster(SIStation,
    SIControlStationMixin):
  product_family = PF.Bs8SiMaster
  product_type = PT.Bs8SiMaster


class Bs11Large(SIStation,
    SIControlStationMixin):
  product_family = PF.Bs11Large
  product_type = PT.Bs11Large


class Bs11Small(SIStation,
    SIControlStationMixin):
  product_family = PF.Bs11Small
  product_type = PT.Bs11Small


class SiPointGolf(SIStation):
  product_family = PF.SiPoint
  product_type = PT.SiPointGolf
  product_type_c1_byte = b'\x90'


class SiPointSportident(SIStation):
  product_family = PF.SiPoint
  product_type = PT.SiPointSportident
  product_type_c1_byte = b'\x92'


class SimSrr(SIStation):
  product_family = PF.SimSrr
  product_type = PT.SimSrr
  has_battery = False

  @property
  def sim_srr_channel(self):
    v = self.mem[52]
    try:
      return si.common.SimSrrFrequencyChannels(v)
    except ValueError:
      return si.common.SimSrrFrequencyChannels.NotSet
  @sim_srr_channel.setter
  def sim_srr_channel(self, C):
    self.mem[52] = C.value

  @property
  def sim_srr_use_mod_d3_protocol(self):
    v = self.mem[63]
    return (v if v in (0, 1) else 255)
  @sim_srr_use_mod_d3_protocol.setter
  def sim_srr_use_mod_d3_protocol(self, v):
    try:
      self.mem[63:64] = v
    except TypeError:
      self.mem[63] = v


class Bs10UfoReaderSiGolf(SIStation):
  product_family = PF.Bs10UfoReaderSiGolf
  product_type = PT.Bs10UfoReaderSiGolf
  has_battery = False


class Bs10UfoReaderSportIdent(SIStation):
  product_family = PF.Bs10UfoReaderSportIdent
  product_type = PT.Bs10UfoReaderSportIdent
  has_battery = False
