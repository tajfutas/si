import collections
import io
import string
import typing

from si.helper import Rollbackable, RollbackableRead, RollbackableBytesRead

BITCHARS = 'oX'


def bbytes(
    b: typing.Iterable[int],
  ) -> bytes:
  bits = []
  # TODO


def bchars(
    b: typing.Iterable[int],
    *,
    bitchars: typing.Union[None, str] = None,
  ) -> str:
  """
  Generate bitdigit charactes for the given iterable of bits
  (integers of range 0--1).

  >>> list(bchars([0,1,1,1]))
  ['o', 'X', 'X', 'X']
  >>> ''.join(bchars(ibits(b'\x0F')))
  'ooooXXXX'
  >>> ''.join(bchars(ibits(b'\x0F'), bitchars='01'))
  '00001111'
  """
  bitchars = bitchars or BITCHARS
  if not hasattr(b, '__next__'):
    b = iter(b)
  while True:
    bit = next(b)
    yield bitchars[bit]


def ibits(
    i: typing.Iterable[int],
    reverse: bool = False,
  ) -> typing.Iterator[int]:
  """
  Generate bits from the given iterable that should generate
  integers of range 0--255 (bytes, bytearray, ...).

  >>> list(ibits(b'\x01\x02'))
  [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0]
  >>> list(ibits(b'\x01\x02', reverse=True))
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
  >>> list(ibits(reversed(b'\x01\x02')))
  [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
  >>> list(ibits(reversed(b'\x01\x02'), reverse=True))
  [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
  """
  bitgen = iter if reverse else reversed
  yield from ((x & 2**j) >> j for x in i
      for j in bitgen(range(8)))


def ihex(
    i: typing.Iterable[int],
    *,
    space: str = ' ',
  ) -> str:
  """
  Generate hexadecimal strings from the given iterable that
  should generate integers of range 0--255
  (bytes, bytearray, ...).

  >>> list(ihex([1,64,100,255]))
  ['01', '40', '64', 'FF']
  >>> ' '.join(ihex(b'hello world'))
  '68 65 6C 6C 6F 20 77 6F 72 6C 64'
  """
  if not hasattr(i, '__next__'):
    i = iter(i)
  while True:
    v = next(i)
    yield '{:0>2X}'.format(v)


def sbits(
    s: typing.Iterable[str],
    *,
    bitchars: typing.Union[None, str] = None,
    ignored: str = ' _|',
    strict: bool = False,
  ) -> typing.Iterator[int]:
  """
  Generate bit integers from the given iterable that should
  yield character strings of bitdigits.

  Default ignored charaters are whitespace, underscore and
  vertical bar. This can be customized with the ignored
  parameter.

  What is considered a bitdigit could be customized with the
  bitchars parameter (default 'oX'). Note that matching is
  case sensitive.

  Iteration ends immediatelly if an invalid character is
  encountered. If strict is True then a ValueError gets raised.

  >>> list(sbits('XooX | ooXo'))
  [1, 0, 0, 1, 0, 0, 1, 0]
  >>> list(sbits('XooX & ooXo'))
  [1, 0, 0, 1]
  >>> list(sbits('XooX & ooXo', strict=True))
  Traceback (most recent call last):
    ...
  ValueError: expected a bitdigit (oX) instead of: '&'
  """
  bitchars = bitchars or BITCHARS
  efs = 'expected a bitdigit ({}) instead of: {!r}'
  if strict:
    exc_cls = ValueError
  else:
    exc_cls = StopIteration
  for chunk in s:
    for c in chunk:
      if c in ignored:
        continue
      elif c not in bitchars:
        raise exc_cls(efs.format(bitchars, c))
      else:
        yield bitchars.index(c)


def sints(
    s: typing.Iterable[str],
    *,
    ignored: str = ' _|',
    strict: bool = True,
  ) -> typing.Iterator[int]:
  """
  Generate integers from the given iterable that should yield
  character strings of hexdigit pairs.

  Default ignored charaters are whitespace, underscore and
  vertical bar. This can be customized with the ignored
  parameter.

  Iteration ends immediatelly if an invalid character is
  encountered. If strict is True then a ValueError gets raised.

  If itereation ends but the last hexdigit ends up without a
  pair then a ValueError gets raised.

  >>> list(sints(['01', '40', '64', 'FF']))
  [1, 64, 100, 255]
  >>> bytes(sints('68 65 6C 6C 6F 20 77 6F 72 6C 64'))
  b'hello world'
  >>> bytes(sints('68 65 !! 6C 6F 20 77 6F 72 6C 64'))
  Traceback (most recent call last):
    ...
  ValueError: expected a hexdigit instead of: '!'
  >>> bytes(sints('68 65 !! 6C 6F', strict=False))
  b'he'
  """
  efs = 'expected a hexdigit instead of: {!r}'
  if strict:
    exc_cls = ValueError
  else:
    exc_cls = StopIteration
  error = None
  first_c = ''
  for chunk in s:
    for c in chunk:
      if c in ignored:
        continue
      elif c not in string.hexdigits:
        error = exc_cls(efs.format(c))
        break
      elif not first_c:
        first_c = c
      else:
        yield int(first_c + c, 16)
        first_c = ''
    if error:
      break
  if first_c:
    efs = 'last character without pair: {!r}'
    raise ValueError(efs.format(first_c))
  elif error:
    raise error








def str2bits(s: typing.Union[str, typing.io], *,
    bitchars: typing.Union[int, None] = None,
    from_left: bool = False,
    octets: typing.Union[int, None, type(...)] = None,
    space: str = ' ',
    strict: typing.Union[None, bool] = None,
  ) -> bytes:
  """
  Convert a string of bitchars to a bytes object or return a
  bytes object from a stream that has bitchars in it. Note that
  the stream must be seekable and tellable.

  For more info see bitchars_as_booleans().

  >>> str2bits('X ooooXXXX XoXoXoXo')
  b'\x01\x0f\xaa'

  The default bit order is from right to left but that could be
  chenged with a truthy from_left parameter.

  >>> str2bits('XooooXXX XXoXoXoX o', from_left=True)
  b'\x87\xd5\x00'
  >>> str2bits('XXX')
  b'\x07'
  >>> str2bits('XXX', from_left=True)
  b'\xe0'

  Spaces are ignored between byte values. The space parameter
  defines the space string (default ' ').

  What is considered a bitdigit could be customized with the
  bitchars parameter (default 'oX'). Note that matching is
  case sensitive.

  >>> str2bits('1_00001111_10101010', space='_', bitchars='01')
  b'\x01\x0f\xaa'

  When called with a string, strict mode is on by default.

  >>> s = 'X ooooXXXX XoXoXoXo 3F 34'
  >>> str2bits(s)
  Traceback (most recent call last):
    ...
  ValueError: expected a bitdigit (oX): '3'
  >>> str2bits(s, strict=False)
  b'\x01\x0f\xaa'

  When called with a stream object then strict mode is off by
  default.

  >>> stream = io.StringIO(s)
  >>> str2bits(stream)
  b'\x01\x0f\xaa'
  >>> stream.read()
  ' 3F 34'
  >>> stream.seek(0)
  0
  >>> str2bits(stream, octets=9)
  b'\x01\x0f'
  >>> stream.read()
  ' XoXoXoXo 3F 34'
  """
  bitchars = bitchars or BITCHARS
  if octets == ...:
    octets = None
  if not hasattr(s, 'read'):
    s = io.StringIO(s)
    if strict is None:
      strict = True
  else:
    if strict is None:
      strict = False
  full_fb = s.tell()
  bools = list(bitchars_as_booleans(s, bitchars=bitchars,
      octets=octets, space=space, strict=strict))
  i = 0
  num_bytes, num_bits = None, None
  if octets:
    rem = len(bools) % octets
    if rem:
      s.seek(full_fb)
      efs = ('expected zero as number of booleans modulo '
          'modulo octets: {} mod {} == {} != 0')
      raise ValueError(efs.format(len(bools), octets, rem))
  else:
    octets = len(bools)
  result = []
  num_bytes, num_bits = 0, 0
  while bools:
    if num_bytes == 0 and num_bits == 0:
      num_bytes, num_bits = divmod(octets, 8)
    if ((from_left and num_bytes)
        or (not from_left and not num_bits and num_bytes)):
      bits, bools = bools[:8], bools[8:]
      num_bytes -= 1
    elif ((not from_left and num_bits)
        or (from_left and not num_bytes and num_bits)):
      bits, bools = bools[:num_bits], bools[num_bits:]
      num_bits = 0
    missing_bits = [False] * (8 - len(bits))
    if missing_bits:
      if from_left:
        bits = bits + missing_bits
      else:
        bits = missing_bits + bits
    result.append(sum(b*2**(7-i) for i, b in enumerate(bits)))
  return bytes(result)


def str2bytes(s: typing.Union[str, typing.io], *,
    octets: typing.Union[int, None, type(...)] = None,
    space: str = ' ',
    strict: typing.Union[None, bool] = None,
  ) -> bytes:
  """
  Convert a string of hexadecimal vales to a bytes object
  or return a bytes object from a stream that has hexadecimal
  characters in it. Note that the stream must be seekable and
  tellable.

  For more info see hexdigits_as_integers().

  >>> s = '68 65 6C 6C 6F 20 77 6F 72 6C 64'
  >>> str2bytes(s)
  b'hello world'

  Spaces are ignored between byte values. The space parameter
  defines the space string (default ' ').

  >>> s = s.replace(' ', '_')
  >>> s
  '68_65_6C_6C_6F_20_77_6F_72_6C_64'
  >>> str2bytes(s, space='_')
  b'hello world'

  When called with a string, strict mode is on by default.

  >>> s = '68 65 6C 6C6F 2077 6 F 72 6C 64 Hello World!'
  >>> str2bytes(s)
  Traceback (most recent call last):
    ...
  ValueError: expected a hexdigit (0123456789abcdefABCDEF): 'H'
  >>> str2bytes(s, strict=False)
  b'hello world'

  When called with a stream object then strict mode is off by
  default.

  >>> stream = io.StringIO(s)
  >>> str2bytes(stream)
  b'hello world'
  >>> stream.read()
  ' Hello World!'
  >>> stream.seek(0)
  0
  >>> str2bytes(stream, octets=5*8)
  b'hello'
  >>> stream.read()
  ' 2077 6 F 72 6C 64 Hello World!'
  """
  return bytes(x for x in hexdigits_as_integers(s,
      octets=octets, space=space, strict=strict))
