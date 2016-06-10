import _thread

import serial

import si

class Connection:

  def __init__(self, station, port, baudrate=4800):
    self.station = station
    self.port = port
    self.baudrate = baudrate
    self.running = None
    self.serial = None
    self.in_buf = None

  def read(self, n=1):
    data = self.serial.read(n)
    self.in_buf.extend(data)
    return data

  def write(self, data):
    return self.serial.write(data)

  def proto_module(self):
    if self.station.vmem_legacy_protocol_mode:
      return si.legproto
    else:
      return si.extproto

  def attach(self):
    _thread.start_new_thread(self._attach, ())

  def _attach(self):
    with serial.Serial(self.port, baudrate=self.baudrate) as s:
      self.serial = s
      self.running = True
      while self.running:
        self.in_buf = bytearray()
        self.handle()
    self.in_buf = None
    self.serial = None

  def handle(self):
    char = self.proto_module().Char(self.read())
    subhandler_name = 'handle_{}'.format(char.name.lower())
    return getattr(self, subhandler_name)()

  def handle_wakeup(self):
    pass

  def handle_stx(self):
    m = self.proto_module()
    cmd_byte = self.read()
    if cmd_byte == m.Char.STX.value:
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


class VirtualStation(Connection):

  def handle_stx(self):
    super().handle_stx()
    m = self.proto_module()
    parts = m.split_instr(self.in_buf)
    cmd = m.Cmd(parts.cmd_byte)
    instr = self.station.instr[cmd]  # experimental
    resp = instr.respond(parts, self.station)
    self.write(resp)


