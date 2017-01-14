import typing

from . import Protocol
from .bits import Cmd

def get_protocol_from_cmd(
    cmd: typing.Union[Cmd, bytes, int]
  ) -> Protocol:
  if hasattr(cmd, 'value'):
    cmd = cmd.value
  elif isinstance(cmd, int):
    cmd = bytes([cmd])
  assert len(cmd) == 1
  return Protocol(cmd >= b'\x80' and cmd != b'\xc4')

