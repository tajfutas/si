__all__ = [
  'command',
  'response',
]

from ._common import LegacyInstruction, codec
LegacyInstruction.__module__ = __name__
from . import command
from . import response


del _common
