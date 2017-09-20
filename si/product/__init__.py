__all__ = [
  'bs',
]

from ._base import BS11_LOOP_ANTENNA_SN, MsMode, \
    ProductFamily, ProductType, SysAddr

# Imported by the main module to avoid import recursion and
# the following exception:
# AttributeError: module 'si.codec.sysdata' has no attribute
# 'serialnumber'
#from . import bs
