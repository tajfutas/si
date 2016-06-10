import datetime
import math
import struct

import si

PF = si.common.ProductFamily
PT = si.common.ProductType


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

  SYSDATA_SIZE = 128

  product_family = PF.NotSet
  product_type = PT.NotSet
  product_type_c1_byte = b'\x00'

  attached_srr_module = False
  has_battery = True
  has_realtime_clock = True
  realtime_clock_enabled = True

  additional_extproto_instructions = frozenset((  # experimental
      si.extproto.GetSystemData,
      si.extproto.SetMsMode,
      ))

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
    inst.sysdata[:] = bb
    return inst

  def __init__(self):
    self._sysdata = memoryview(bytearray(self.SYSDATA_SIZE))
    self._sysdata[12] = self.product_family.value
    self.transfer_mode = si.common.MSMode.Master  # experimental
    self.instr = {i.CMD: i for c in self.__class__.__mro__
        if hasattr(c, 'additional_extproto_instructions')
        for i in c.additional_extproto_instructions
        }

  @property
  def sysdata(self):
    return self._sysdata

  def sysdata_str(self):
    return '\n'.join(' '.join('{:>02X}'.format(x)
        for x in self.sysdata[16*c : 16*c + 16])
        for c in range(len(self.sysdata) // 16))

  @property
  def vmem_serial_number(self):
    bb = self.sysdata[0:4].tobytes()
    return struct.unpack('>I', bb)[0]
  @vmem_serial_number.setter
  def vmem_serial_number(self, v):
    self.sysdata[0:4] = struct.pack('>I', v)

  @property
  def vmem_bus_type_byte(self):
    return self.sysdata[4:5].tobytes()
  @vmem_bus_type_byte.setter
  def vmem_bus_type_byte(self, b):
    self.sysdata[4:5] = b

  @property
  def vmem_firmware_version(self):
    v = self.sysdata[5:8].tobytes()
    if v != b'\x00\x00\x00':
      return v.decode('ascii')
  @vmem_firmware_version.setter
  def vmem_firmware_version(self, s):
    self.sysdata[5:8] = '{:0>3}'.format(s).encode('ascii')
  @property
  def vmem_firmware_version_value(self):
    try:
      return int(self.firmware_version)
    except:
      return 0
    return self.sysdata[5:8].tobytes().decode('ascii')
  @vmem_firmware_version_value.setter
  def vmem_firmware_version_value(self, v):
    self.firmware_version = str(v)

  @property
  def vmem_production_date(self):
    bb = self.sysdata[8:11].tobytes()
    try:
      return si.common.from_sidate(bb)
    except ValueError:
      pass
  @vmem_production_date.setter
  def vmem_production_date(self, D):
    self.sysdata[8:11] = si.common.to_sidate(D)



class SIControlStationMixin:

  @property
  def board_version(self):
    return self.sysdata[12] & 0b1111

  @property
  def vmem_backup_memory_size(self):
    v = self.sysdata[13]
    return (0 if v == 255 else v)
  @vmem_backup_memory_size.setter
  def vmem_backup_memory_size(self, v):
    self.sysdata[13] = v

  @property
  def vmem_battery_date(self):
    bb = self.sysdata[21:24].tobytes()
    try:
      return si.common.from_sidate(bb)
    except ValueError:
      pass
  @vmem_battery_date.setter
  def vmem_battery_date(self, D):
    self.sysdata[21:24] = si.common.to_sidate(D)

  @property
  def vmem_battery_capacity(self):
    bb = self.sysdata[24:28].tobytes()
    v = struct.unpack('>I', bb)[0] / 3600
    return (v if v < 100000 else 0)
  @vmem_battery_capacity.setter
  def vmem_battery_capacity(self, v):
    self.sysdata[24:28] = struct.pack('>I', round(v * 3600))

  @property
  def vmem_backup_memory_pointer(self):
    return (self.sysdata[28:30].tobytes()
        + self.sysdata[33:35].tobytes())
  @vmem_backup_memory_pointer.setter
  def vmem_backup_memory_pointer(self, bb):
    assert len(bb) == 4
    self.sysdata[28:30] = bb[:2]
    self.sysdata[33:35] = bb[2:]

  @property
  def vmem_ewd_counter(self):
    return self.sysdata[49]
  @vmem_ewd_counter.setter
  def vmem_ewd_counter(self, v):
    self.sysdata[49] = v

  @property
  def vmem_card6_with_112_records(self):
    return (self.sysdata[51] == 255)
  @vmem_card6_with_112_records.setter
  def vmem_card6_with_112_records(self, bo):
    self.sysdata[51] = (255 if bo else 0)

  @property
  def vmem_battery_capacity_consumed(self):
    if self.sysdata[52] == 255:
      return -1.0
    else:
      bb = self.sysdata[52:56].tobytes()
      return struct.unpack('>I', bb)[0] / 3600
  @vmem_battery_capacity_consumed.setter
  def vmem_battery_capacity_consumed(self, v):
    bb = struct.pack('>I', round(v * 3600))
    self.sysdata[52:56] = bb

  @property
  def vmem_backup_memory_full(self):
    return self.sysdata[61] & 0b1111111
  @vmem_backup_memory_full.setter
  def vmem_backup_memory_full(self, v):
    assert (0 <= v <= 127)
    self.sysdata[61] = (self.sysdata[61] & 0b10000000) + v

  @property
  def vmem_eco_mode(self):
    return (self.sysdata[78] == 1 and self.sysdata[79] == 5)
  @vmem_eco_mode.setter
  def vmem_eco_mode(self, bo):
    if bo:
      self.sysdata[78:80] = b'\x01\x05'
    else:
      self.sysdata[78:80] = b'\x00\x00'

  @property
  def vmem_battery_voltage(self):
    bb = self.sysdata[80:82].tobytes()
    v = struct.unpack('>H', bb)[0]
    if v > 13100:
      v /= 131
    return math.floor(v) / 100
  @vmem_battery_voltage.setter
  def vmem_battery_voltage(self, v):
    v *= 100
    v *= 131
    self.sysdata[80:82] = struct.pack('>H', math.floor(v))

  @property
  def vmem_battery_temperature(self):
    bb = self.sysdata[82:84].tobytes()
    v = struct.unpack('>H', bb)[0]
    if v >= 25800:
      return (v - 25800) / 92
    else:
      return v / 10
  @vmem_battery_temperature.setter
  def vmem_battery_temperature(self, v):
    v = round(v * 92) + 25800
    self.sysdata[82:84] = struct.pack('>H', math.floor(v))

  @property
  def vmem_boot_version(self):
    v = self.sysdata[96:100].tobytes()
    if v != b'\x00\x00\x00\x00':
      return v.decode('ascii')
  @vmem_boot_version.setter
  def vmem_boot_version(self, s):
    self.sysdata[96:100] = '{:0>4}'.format(s).encode('ascii')

  @property
  def vmem_allowed_function_modes(self):
    return self.sysdata[100:108].tobytes()
  @vmem_allowed_function_modes.setter
  def vmem_allowed_function_modes(self, bb):
    self.sysdata[100:108] = bb

  @property
  def vmem_allow_gate_mode(self):
    if (10 <= self.board_version
        and 332 <= self.vmem_firmware_version_value):
      return (self.sysdata[112] & 0b10000 == 0b10000)
    else:
      return False
  @vmem_allow_gate_mode.setter
  def vmem_allow_gate_mode(self, bo):
    if self.board_version < 10:
      errmsg = 'board version is lower than 10'
      raise TypeError(errmsg)
    elif self.vmem_firmware_version_value <  332:
      errmsg = 'firmware version lower than 332'
      raise TypeError(errmsg)
    v = bool(bo) * 0b10000
    self.sysdata[112] = (self.sysdata[112] & 0b11101111) + v

  @property
  def vmem_acoustic_signal(self):
    return (self.sysdata[115] & 0b100 == 0b100)
  @vmem_acoustic_signal.setter
  def vmem_acoustic_signal(self, bo):
    v = bool(bo) * 0b100
    self.sysdata[115] = (self.sysdata[115] & 0b11111011) + v

  @property
  def vmem_optical_signal1(self):
    return (self.sysdata[115] & 0b1 == 0b1)
  @vmem_optical_signal1.setter
  def vmem_optical_signal1(self, bo):
    v = bool(bo) * 0b1
    self.sysdata[115] = (self.sysdata[115] & 0b11111110) + v

  @property
  def vmem_optical_signal2(self):
    if (10 <= self.board_version):
      return (self.sysdata[115] & 0b10 == 0b10)
    else:
      return False
  @vmem_optical_signal2.setter
  def vmem_optical_signal2(self, bo):
    if self.board_version < 10:
      errmsg = 'board version is lower than 10'
      raise TypeError(errmsg)
    v = bool(bo) * 0b10
    self.sysdata[115] = (self.sysdata[115] & 0b11111101) + v

  @property
  def vmem_operating_mode(self):
    v = self.sysdata[113] & 0b11111
    try:
      return si.common.OperatingMode(v)
    except ValueError:
      return si.common.OperatingMode.Unknown
  @vmem_operating_mode.setter
  def vmem_operating_mode(self, O):
    v = O.value
    assert (0 <= v <= 0b11111)
    self.sysdata[113] = (self.sysdata[113] & 0b11100000) + v

  @property
  def vmem_srr_mode(self):
    if ((16 < self.vmem_operating_mode.value
            and 10 <= self.board_version)
        or (7 <= self.board_version
            and 588 <= self.vmem_firmware_version_value)):
      v = self.sysdata[113] & 0b11000000
      return sr_common.AirPlusRadioMode(v >> 6)
  @vmem_srr_mode.setter
  def vmem_srr_mode(self, M):
    if 10 <= self.board_version:
      if self.vmem_operating_mode.value <= 16:
        errmsg = 'bad operating mode'
        raise TypeError(errmsg)
    elif 7 <= self.board_version:
      if self.vmem_firmware_version_value < 588:
        errmsg = 'firmware version lower than 588'
        raise TypeError(errmsg)
    if not isinstance(M, sr_common.AirPlusRadioMode):
      M = sr_common.AirPlusRadioMode(M)
    v = M.value << 6
    self.sysdata[113] = (self.sysdata[113] & 0b111111) + v

  @property
  def vmem_beacon_mode(self):
    if 10 <= self.board_version:
      return si.common.BeaconTimingMode(self.sysdata[113] >> 5)
    else:
      return si.common.BeaconTimingMode.Unknown
  @vmem_beacon_mode.setter
  def vmem_beacon_mode(self, M):
    if self.board_version < 10:
      errmsg = 'board version is lower than 10'
      raise TypeError(errmsg)
    if not isinstance(M, sr_common.BeaconTimingMode):
      assert M in (0, 1)
      M = sr_common.BeaconTimingMode(M)
    v = M.value << 5
    self.sysdata[113] = (self.sysdata[113] & 0b11011111) + v

  @property
  def vmem_code_number(self):
    if 10 <= self.board_version:
      vh = (self.sysdata[115] & 0b1000000) << 2
    else:
      vh = (self.sysdata[115] & 0b11000000) << 2
    return vh + self.sysdata[114]
  @vmem_code_number.setter
  def vmem_code_number(self, v):
    if self.board_version < 10:
      maxv = 511
    else:
      maxv = 1023
    assert (0 <= v <= maxv)
    vh, vl = divmod(v, 256)
    vh_ = vh << 6
    self.sysdata[115] = (self.sysdata[115] & 0b111111) + vh_
    self.sysdata[114] = vl

  @property
  def vmem_code_number_cn(self):
    return struct.pack('B', self.vmem_code_number)

  @property
  def vmem_code_number_cn10(self):
    return struct.pack('>H', self.vmem_code_number)


  @property
  def vmem_airplus_special_mode(self):
    dcontrol = si.common.OperatingMode.DControl
    if self.vmem_operating_mode == dcontrol:
      code_number = self.vmem_code_number
      try:
        return si.common.AirPlusSpecialMode(code_number)
      except ValueError:
        pass
    return si.common.AirPlusSpecialMode.NotSetOrDisabled

  @property
  def vmem_legacy_protocol_mode(self):
    b = 0b1
    return (self.sysdata[116] & b != b)
  @vmem_legacy_protocol_mode.setter
  def vmem_legacy_protocol_mode(self, bo):
    bc = 0b11111110
    v = (not bool(bo))
    self.sysdata[116] = (self.sysdata[116] & bc) + v

  @property
  def vmem_auto_send_mode(self):
    b = 0b10
    return (self.sysdata[116] & b == b)
  @vmem_auto_send_mode.setter
  def vmem_auto_send_mode(self, bo):
    bc = 0b11111101
    v = bool(bo) << 1
    self.sysdata[116] = (self.sysdata[116] & bc) + v

  @property
  def vmem_communication_mode(self):
    b = 0b100
    return (self.sysdata[116] & b == b)
  @vmem_communication_mode.setter
  def vmem_communication_mode(self, bo):
    bc = 0b11111011
    v = bool(bo) << 2
    self.sysdata[116] = (self.sysdata[116] & bc) + v

  @property
  def vmem_sprint_mode(self):
    b = 0b1000
    return (self.sysdata[116] & b == b)
  @vmem_sprint_mode.setter
  def vmem_sprint_mode(self, bo):
    bc = 0b11110111
    v = bool(bo) << 3
    self.sysdata[116] = (self.sysdata[116] & bc) + v

  @property
  def vmem_stop_if_backup_full(self):
    b = 0b100000
    return (self.sysdata[116] & b == b)
  @vmem_stop_if_backup_full.setter
  def vmem_stop_if_backup_full(self, bo):
    bc = 0b11011111
    v = bool(bo) << 5
    self.sysdata[116] = (self.sysdata[116] & bc) + v

  @property
  def vmem_last_config_modification(self):
    bb = self.sysdata[117:123].tobytes()
    try:
      return si.common.from_sitime63(bb)
    except ValueError:
      pass
  @vmem_last_config_modification.setter
  def vmem_last_config_modification(self, T):
    self.sysdata[117:123] = si.common.to_sitime63(T)

  @property
  def vmem_operating_time(self):
    bb = self.sysdata[126:128].tobytes()
    v = struct.unpack('>H', bb)[0]
    v = min(max(v, 2), 5759)
    return datetime.timedelta(seconds=v)
  @vmem_operating_time.setter
  def vmem_operating_time(self, T):
    if hasattr(T, 'total_seconds'):
      T = int(T.total_seconds())
    assert (2 <= T <= 5759)
    self.sysdata[126:128] = struct.ack('>H', T)


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
  def sysdata_matches(cls, bb):
    if not isinstance(bb, bytes):
      bb = bytes(bb)
    m0 = super().sysdata_matches(bb)
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
  def sysdata_matches(cls, bb):
    if not isinstance(bb, bytes):
      bb = bytes(bb)
    m0 = super().sysdata_matches(bb)
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
  def vmem_sim_srr_channel(self):
    v = self.sysdata[52]
    try:
      return si.common.SimSrrFrequencyChannels(v)
    except ValueError:
      return si.common.SimSrrFrequencyChannels.NotSet
  @vmem_sim_srr_channel.setter
  def vmem_sim_srr_channel(self, C):
    self.sysdata[52] = C.value

  @property
  def vmem_sim_srr_use_mod_d3_protocol(self):
    v = self.sysdata[63]
    return (v if v in (0, 1) else 255)
  @vmem_sim_srr_use_mod_d3_protocol.setter
  def vmem_sim_srr_use_mod_d3_protocol(self, v):
    try:
      self.sysdata[63:64] = v
    except TypeError:
      self.sysdata[63] = v


class Bs10UfoReaderSiGolf(SIStation):
  product_family = PF.Bs10UfoReaderSiGolf
  product_type = PT.Bs10UfoReaderSiGolf
  has_battery = False


class Bs10UfoReaderSportIdent(SIStation):
  product_family = PF.Bs10UfoReaderSportIdent
  product_type = PT.Bs10UfoReaderSportIdent
  has_battery = False
