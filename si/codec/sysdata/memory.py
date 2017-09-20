# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L6176-L6765)


from . import serialnumber
from . import bustype
from . import firmwareversion
from . import productiondate
from . import productconfiguration
from . import producttype
from . import productfamily
from . import boardversion


sysadr = {
  'SerialNumber': ('BN3', 'BN2', 'BN1', 'BN0'),
  'BusType': ('CFG2',),
  'FirmwareVersion': ('SV2', 'SV1', 'SV0'),
  'ProductionDate': ('PROD_YEAR', 'PROD_MONTH', 'PROD_DAY'),
  'ProductConfiguration': ('CFG1', 'CFG0'),
  'ProductType': ('CFG0', 'CFG1', 'CFG2',
      'BN3', 'BN2', 'BN1', 'BN0'),
  'ProductFamily': ('CFG0',),
  'BoardVersion': ('CFG0',),
}
