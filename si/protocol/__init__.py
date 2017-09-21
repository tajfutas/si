__all__ = [
    'extended',
    'legacy',
    ]


from ._common import Mode, ProtoChar
Mode.__module__ = __name__
ProtoChar.__module__ = __name__
from . import extended
from . import legacy


del _common
