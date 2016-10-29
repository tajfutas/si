import asyncio
from enum import Enum

import serial
import serial.aio

import si

class AutoSendException(Exception): pass


class Protocol(asyncio.Protocol):

  def __init__(self, cnxn, *args, **kwargs):
    super.__init__(*args, **kwargs)
    self.cnxn = cnxn
    self.loop = cnxn.loop
    self.transport = None
    self.curr_instr_data = None

  @property
  def proto_module(self):
    if self.cnxn.station.legacy_protocol_mode:
      return si.legproto
    else:
      return si.extproto

  def connection_made(self, transport):
    self.transport = transport
    self.running = self.loop.create_future()
    print('port opened', transport)
    transport.serial.rts = False
    transport.write(b'hello world\n')

  def data_received(self, data):
    print('data received', repr(data))
    remaining_data = data
    while True:
      if self.curr_instr_data is None:
        instr_data = self.proto_module.Record()
        self.curr_instr_data = instr_data
      try:
        self.curr_instr_data.send(remaining_data)
      except si.proto.RecordOverflow as ovrflw:
        self.cnxn.instr_data_received(self.curr_instr_data)
        self.curr_instr_data = None
        remaining_data = ovrflw.data
      else:
        if self.curr_instr_data.complete:
          self.cnxn.instr_data_received(self.curr_instr_data)
          self.curr_instr_data = None
        break

  def connection_lost(self, exc):
    print('port closed')
    self.running.set_result(False)

  def pause_writing(self):
    print('pause writing')
    print(self.transport.get_write_buffer_size())

  def resume_writing(self):
    print(self.transport.get_write_buffer_size())
    print('resume writing')



class Connection:

  def __init__(self, station, port, baudrate=4800, loop=None):
    self.loop = loop or asyncio.get_event_loop()
    self.station = station
    self.port = port
    self.baudrate = baudrate
    self.running = None
    self.serial = None
    self.in_buf = None
    self._thread = None

  async def attach(self, protocol=None):
    protocol_class = protocol or Protocol
    protocol_factory = lambda self=self: protocol(self)
    transport, protocol = serial.aio.create_serial_connection(
        self.loop, protocol, self.port, baudrate=self.baudrate)
    self.loop.run_until_complete(coro)
    self.loop.run_until_complete(protocol.running)
    self.loop.close()



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
    #CMD = self.proto_module.Cmd[]


  def handle_stx(self):
    super().handle_stx()
    m = self.proto_module
    parts = m.split_instr(self.in_buf)
    cmd = m.Cmd(parts.cmd_byte)
    instr = self.station.instr[cmd]  # experimental
    pinstr = instr.precv(parts, self.station)
    if pinstr is not None:
      self.write(pinstr)
