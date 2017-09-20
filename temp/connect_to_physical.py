"""
DBISAM ODBC Connection

Usage:
  connect_to_physical <comX>
"""

import os
import sys

import docopt

import si

args = docopt.docopt(__doc__)
station = si.station.Bsm7()
cnxn = si.connection.PhysicalStation(station,  args['<comX>'])
cnxn.attach()
os.environ['PYTHONINSPECT'] = '1'
