__all__ = [
    'codec',
    'common',
    'exc',
    'product',
    'protocol',
    'siid',
    'srr',
    'utils'
    ]

# The following is the import hierarchy of the si module;
# no module should import from other modules below itself,
# but can import from any other above:
from . import utils
from . import common
from . import exc
from . import siid
from . import srr
from . import codec
from . import protocol
from . import product

# The following modules' contents are to be found in the
# corresponding module tree:
del codec.instruction.__protocol
del codec.instruction.extended.__protocol
del codec.instruction.legacy.__protocol
del codec.sysdata.__product
