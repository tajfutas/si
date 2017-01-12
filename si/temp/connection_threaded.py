import time
import threading

import serial
import serial.threaded

import si

class AutoSendException(Exception): pass


class Connection:

  class ConnectionThread(threading.Thread):
    def __init__(self, cnxn):
      super().__init__()
      self.cnxn = cnxn

    def run(self):
      return self.cnxn.__class__._attach(self.cnxn)

  def __init__(self, station, port, baudrate=4800):
    self.station = station
    self.port = port
    self.baudrate = baudrate
    self.running = None
    self.serial = None
    self.in_buf = None
    self._thread = None

  def _attach(self):
    with serial.Serial(self.port, baudrate=self.baudrate) as s:
      self.serial = s
      self.after_attached()
      self.running = True
      while self.running:
        try:
          self.in_buf = bytearray()
          self.handle()
        except AutoSendException:
          print('throw works')  # experimental
    self.in_buf = None
    self.serial = None
    self._thread = None

  def after_attached(self):
    pass

  def attach(self):
    self._thread = self.ConnectionThread(self)
    self._thread.start()
    return self._thread

  def handle(self):
    #try:  # experimental
      #while not self.seriaL.in_waiting:
      #  time.sleep(0.001)
      char = self.proto_module.proto.Char(self.read())
      subhandler_name = 'handle_{}'.format(char.name.lower())
      return getattr(self, subhandler_name)()
    #except:
    #  pass

  def handle_wakeup(self):
    pass

  def handle_stx(self):
    m = self.proto_module
    cmd_byte = self.read()
    if cmd_byte == m.proto.Char.STX.value:
      # Two STX was send to ensure STX detection
      cmd_byte = self.read()
    cmd = m.Cmd(cmd_byte)
    if m == si.extproto:
      length = self.read()[0]
      data = self.read(length)
      crc = self.read(2)
      # TODO
      # assert crc == struct.pack('>H',
      #   si_common.get_crc(data_[:2+length]))
      etx = self.read()


  def proto_module(self):
    if self.station.legacy_protocol_mode:
      return si.legproto
    else:
      return si.extproto

  def read(self, n=1):
    data = self.serial.read(n)
    self.in_buf.extend(data)
    return data

  def write(self, data):
    return self.serial.write(data)


class VirtualStation(Connection):

  def handle_stx(self):
    super().handle_stx()
    m = self.proto_module
    parts = m.split_instr(self.in_buf)
    cmd = m.Cmd(parts.cmd_byte)
    instr = self.station.instr[cmd]  # experimental
    sinstr = instr.srecv(parts, self.station)
    if sinstr is not None:
      self.write(sinstr)



class PhysicalStation(Connection):

  def __init__(self, station, port, baudrate=4800):
    super().__init__(station, port, baudrate)
    self.attach()
    ####
    CMD = self.proto_module.Cmd[]


  def handle_stx(self):
    super().handle_stx()
    m = self.proto_module
    parts = m.split_instr(self.in_buf)
    cmd = m.Cmd(parts.cmd_byte)
    instr = self.station.instr[cmd]  # experimental
    pinstr = instr.precv(parts, self.station)
    if pinstr is not None:
      self.write(pinstr)
