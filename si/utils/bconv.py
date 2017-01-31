import string
import typing

from si.boltons.iterutils import chunked_iter


BITCHARS = 'oX'


def bits2chars(
    b: typing.Iterable[int],
    *,
    bitchars: typing.Union[None, str] = None,
  ) -> str:
  """
  Generate bitdigit charactes for the given iterable of bits
  (integers of range 0--1).

  >>> list(bits2chars([0,1,1,1]))
  ['o', 'X', 'X', 'X']
  >>> ''.join(bits2chars(ints2bits(b'\x0F')))
  'ooooXXXX'
  >>> ''.join(bits2chars(ints2bits(b'\x0F'), bitchars='01'))
  '00001111'
  """
  bitchars = bitchars or BITCHARS
  yield from (bitchars[bit] for bit in b)


def bits2ints(
    b: typing.Iterable[int],
  ) -> typing.Iterator[int]:
  """
  Generate integers in range 0-255 from the given iterable that
  should yield bits (integers of range 0--1). Each 8 Bits are
  grouped and a new integer generated from them.

  If itereation ends but there is an undone group remained then
  a ValueError gets raised.

  >>> list(bits2ints([0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]))
  [0, 255]
  >>> list(bits2ints([1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]))
  [128, 1]
  >>> list(bits2ints([1]))
  Traceback (most recent call last):
    ...
  ValueError: undone bitgroup remained
  """
  for bits in chunked_iter(b, 8, fill=None):
    if bits[-1] is None:
      raise ValueError('undone bitgroup remained')
    yield sum(bit*2**(7-i) for i, bit in enumerate(bits))


def bits2str(
    b: typing.Iterable[int],
    groupsize: typing.Union[None, int] = 8,
    *,
    bitchars: typing.Union[None, str] = None,
    space = ' ',
  ) -> str:
  """
  Generate bitdigit charactes for the given iterable of bits
  (integers of range 0--1). Note that the iterable will be fully
  consumed.

  If groupsize parameter is a positive integer then the bits are
  going to get grouped into groups of that sizes. From the
  second and subsequent groups, each substring gets prepended
  with the space string.

  If there is an undone group remained at the end then a
  ValueError gets raised.

  If groupsize is falsy then no groups/check are made.

  >>> bits2str([1,0,0,0,1,1,1,0,1,0,1,0,0,0,0,0])
  'XoooXXXo XoXooooo'
  >>> bits2str([1,0,0,0,1,1,1,0,1,0,1,0,0,0,0,0], space=' | ')
  'XoooXXXo | XoXooooo'
  >>> bits2str([1,0,0,0,1,1,1,0,1,0,1])
  Traceback (most recent call last):
    ...
  ValueError: undone bitgroup remained
  >>> bits2str([1,0,0,0,1,1,1,0,1,0,1], None)
  'XoooXXXoXoX'
  >>> bits2str([1,0,0,0,1,1], 3)
  'Xoo oXX'
  >>> bits2str([1,0,0,0,1,1], 2)
  'Xo oo XX'
  """
  gen = bits2chars(b, bitchars=bitchars)
  if groupsize:
    def subiterator(subgen):
      for i, _bchars in enumerate(
          chunked_iter(subgen, groupsize, fill=None)):
        if _bchars[-1] is None:
          raise ValueError('undone bitgroup remained')
        s = ''.join(_bchars)
        if i:
          yield space + s
        else:
          yield s
    gen = subiterator(gen)
  return ''.join(gen)


def ints2bits(
    i: typing.Iterable[int],
    reverse: bool = False,
  ) -> typing.Iterator[int]:
  """
  Generate bits from the given iterable that should generate
  integers of range 0--255 (bytes, bytearray, ...).

  >>> list(ints2bits(b'\x01\x02'))
  [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0]
  >>> list(ints2bits(b'\x01\x02', reverse=True))
  [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
  >>> list(ints2bits(reversed(b'\x01\x02')))
  [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
  >>> list(ints2bits(reversed(b'\x01\x02'), reverse=True))
  [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
  """
  bitgen = iter if reverse else reversed
  yield from ((x & 2**j) >> j for x in i
      for j in bitgen(range(8)))


def ints2hexes(
    i: typing.Iterable[int],
  ) -> str:
  """
  Generate hexadecimal strings from the given iterable that
  should generate integers of range 0--255
  (bytes, bytearray, ...).

  >>> list(ints2hexes([1,64,100,255]))
  ['01', '40', '64', 'FF']
  >>> ' '.join(ints2hexes(b'hello world'))
  '68 65 6C 6C 6F 20 77 6F 72 6C 64'
  """
  yield from ('{:0>2X}'.format(x) for x in iter(i))


def ints2str(
    i: typing.Iterable[int],
    *,
    space: str = ' ',
  ) -> str:
  """
  Generate string of hexadecimal pairs for the given iterable
  of integers (of range 0-255). Note that the iterable will be
  fully consumed.

  >>> ints2str([1,64,100,255])
  '01 40 64 FF'
  >>> ints2str(b'hello world')
  '68 65 6C 6C 6F 20 77 6F 72 6C 64'
  """
  return space.join(ints2hexes(i))


def str2bits(
    s: typing.Iterable[str],
    *,
    bitchars: typing.Union[None, str] = None,
    ignored: str = ' _|',
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

  >>> list(str2bits('XooX | ooXo'))
  [1, 0, 0, 1, 0, 0, 1, 0]
  >>> list(str2bits('XooX & ooXo'))
  Traceback (most recent call last):
    ...
  ValueError: expected a bitdigit (oX) instead of: '&'
  """
  bitchars = bitchars or BITCHARS
  efs = 'expected a bitdigit ({}) instead of: {!r}'
  for c in (c for e in s for c in e if c not in ignored):
    try:
      yield bitchars.index(c)
    except ValueError:
      raise ValueError(efs.format(bitchars, c))


def str2ints(
    s: typing.Iterable[str],
    *,
    ignored: str = ' _|',
  ) -> typing.Iterator[int]:
  """
  Generate integers from the given iterable that should yield
  character strings of hexdigit pairs.

  Default ignored charaters are whitespace, underscore and
  vertical bar. This can be customized with the ignored
  parameter.

  >>> list(str2ints(['01', '40', '64', 'FF']))
  [1, 64, 100, 255]
  >>> bytes(str2ints('68 65 6C 6C 6F 20 77 6F 72 6C 64'))
  b'hello world'
  >>> bytes(str2ints('68 65 !! 6C 6F 20 77 6F 72 6C 64'))
  Traceback (most recent call last):
    ...
  ValueError: invalid literal for int() with base 16: '!!'
  >>> bytes(str2ints('68 65 5'))
  Traceback (most recent call last):
    ...
  ValueError: last character without pair: '5'
  """
  for chunk in chunked_iter(
      (c for e in s for c in e if c not in ignored),
      2, fill=None):
    if chunk[-1] is None:
      efs = 'last character without pair: {!r}'
      raise ValueError(efs.format(chunk[0]))
    yield int(''.join(chunk), 16)
