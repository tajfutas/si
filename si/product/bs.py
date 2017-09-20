from si import product as _product_
from . import memory as _memory_


class BaseStation:

  MEM_SIZE = 0x1FFFF + 1
  START_ADR = 0x100
  SYSDATA_SIZE = 128

  PRODUCT_FAMILY = _product_.ProductFamily.NotSet

  def __init__(self):
    m = self._memory = _memory_.Memory(
        memoryview(bytearray(self.MEM_SIZE))
    )
    # sysdata is assumed to stay in the first part of memory
    sysdata = self._sysdata = _memory_.SysDataMemory(
        memoryview(m[:self.SYSDATA_SIZE])
    )
    # backup memory is assumed to stay from START_ADR to the end
    backupmemory = self._backup = _memory_.BackupMemory(
        memoryview(m[self.START_ADR:])
    )

    sysdata['ProductFamily'] = self.PRODUCT_FAMILY
  #keep _memory_

  @property
  def backupmemory(self):
    return self._backupmemory

  @property
  def memory(self):
    return self._memory

  @property
  def sysdata(self):
    return self._sysdata
