from . import bconv as _bconv_
from .boltons import iterutils as _iterutils_


def hexview(data, *, encoding='latin1'):
  replaced = {5, 6, 7, 8, 9, 10, 13}
  return '\n'.join(
      f'| {_bconv_.ints2str(chunk):<47} | '
      + bytes(
          (
              (ord(b' ') if x in replaced else x)
              for x in chunk
          )
      ).decode(encoding, errors='replace')
      + ' |'
      for chunk in _iterutils_.chunked_iter(data, 16)
  )
