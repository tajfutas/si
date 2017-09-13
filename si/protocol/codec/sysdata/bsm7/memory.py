  # References:
  # Communication.cs 0917311 (#L6176-L6765)

import types as _types

from . import serialnumber
from . import bustype
from . import firmwareversion
from . import productiondate

ADR_MAP = (
    # Communication.cs 0917311 (#L3034)
    'SerialNumber', # [0:4]
    'SerialNumber',
    'SerialNumber',
    'SerialNumber',
    # Communication.cs 0917311 (#L3052)
    'BusType', # [4:5]
    # Communication.cs 0917311 (#L2995)
    'FirmwareVersion', # [5:8]
    'FirmwareVersion',
    'FirmwareVersion',
    # Communication.cs 0917311 (#L3006)
    'ProductionDate', # [8:11]
    'ProductionDate',
    'ProductionDate',
    # Communication.cs 0917311 (#L3023)
    'ProductConfiguration', # [11:13]
    # ^ Product type C1 byte (includes BoardVersion)
    'ProductConfiguration',
    # ^ Product Family
  )

adr_parts = {}
for _i, _k in enumerate(ADR_MAP):
  adr_parts.setdefault(_k, []).append(_i)
adr_parts = _types.MappingProxyType(
    {k: tuple(v) for k, v in adr_parts.items()})
del _i, _k


del _types
