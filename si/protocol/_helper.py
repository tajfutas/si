import collections
import io
import string
import typing


BITDIGITS = 'oX'


def bitdigits_as_booleans(stream: typing.io, *,
    bitdigits: typing.Union[int, None] = None,
    # http://bugs.python.org/issue29356
    octets: typing.Union[int, None, type(...)] = None,
    space: str = ' ',
    strict: bool = True,
  ) -> typing.Iterator[bool]:
  """
  Yield booleans by reading the stream for bit character pairs

  It is recommended to pass an explicit octets value if the
  length of the data in bits is known beforehand.

  Note that the stream must be seekable and tellable.

  Spaces are ignored between bit values. The space parameter
  defines the space string (default ' ').

  What is considered a bitdigit could be customized with the
  bitdigits parameter (default 'oX'). Note that matching is
  case sensitive.

  >>> s = 'XoXXX'
  >>> stream = io.StringIO(s)
  >>> list(bitdigits_as_booleans(stream))
  [True, False, True, True, True]

  Strict mode is on by default. This means that
  * if octets then EOF expected after the required number of
    bits were read;
  * if no octets then reading should go without invalid
    characters until EOF.

  >>> stream.seek(0)
  0
  >>> list(bitdigits_as_booleans(stream, octets=4))
  Traceback (most recent call last):
    ...
  ValueError: EOF expected
  >>> list(bitdigits_as_booleans(stream, octets=5))
  [True, False, True, True, True]
  >>> s = 'oXXXX XoX Hello World!'
  >>> stream = io.StringIO(s)
  >>> list(bitdigits_as_booleans(stream))
  Traceback (most recent call last):
    ...
  ValueError: expected a bitdigit (oX): 'H'
  >>> stream.read()
  'oXXXX XoX Hello World!'
  >>> stream.seek(0)
  0
  >>> list(bitdigits_as_booleans(stream, strict=False))
  [False, True, True, True, True, True, False, True]
  >>> stream.read()
  ' Hello World!'
  """
  bitdigits = bitdigits or BITDIGITS
  if octets == ...:
    octets = None
  c = None
  full_fb = fb = stream.tell()
  while octets is None or -1 < octets:
    if c != space:
      fb = stream.tell()
    c = stream.read(1)
    if c == space:
      continue
    if not c:
      if octets is not None and 0 < octets:
        stream.seek(full_fb)
        raise ValueError('EOF reached unexpectedly')
      break
    elif octets is not None and octets == 0:
      if strict and c:
        stream.seek(full_fb)
        raise ValueError('EOF expected')
      else:
        stream.seek(fb)
        break
    elif c not in bitdigits:
      if strict or (octets is not None and 0 < octets):
        exc_cls = ValueError
        stream.seek(full_fb)
      else:
        exc_cls = StopIteration
        stream.seek(fb)
      efs = 'expected a bitdigit ({}): {!r}'
      raise exc_cls(efs.format(bitdigits, c))
    else:
      yield bool(int(bitdigits.index(c)))
      if octets is not None:
        octets -= 1


def bits(bytes_: bytes,
    reversed_bytes: bool = False,
    reversed_bits: bool = False
  ) -> typing.Iterator[int]:
  """
  Yield bits of the given bytes object

  >>> list(bits(b'\x0F\xAA'))
  [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0]
  >>> list(bits(b'\x0F\xAA', reversed_bytes=True))
  [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1]
  >>> list(bits(b'\x0F\xAA', reversed_bits=True))
  [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1]
  >>> list(bits(b'\x0F\xAA', reversed_bytes=True,
  ...     reversed_bits=True))
  [0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0]

  """
  B_it = reversed if reversed_bytes else iter
  b_it = iter if reversed_bits else reversed
  yield from ((B & 2**i) >> i for B in B_it(bytes_)
      for i in b_it(range(8)))


def bits2str(bytes_: bytes,
    octets: typing.Union[int, None, type(...)] = None,
    space: str = None,
    chars: typing.Sequence[str] = 'oX',
    from_left: bool = False,
  ) -> str:
  """
  Convert a bytes object to string of bit values.

  >>> bits2str(b'\x0F')
  'ooooXXXX'

  Pad bits can be trimmed by setting an explicit octets value.
  Octets default is the lenght of the bytes in octets.

  >>> bits2str(b'\x0F', octets=6)
  'ooXXXX'

  If octets modulo 8 is zero then spaces are added between the
  bytes. Otherwise no spaces are added. The default behavior
  can be overridden with an explicit space string.

  >>> bits2str(b'\x0F\xaa')
  'ooooXXXX XoXoXoXo'
  >>> bits2str(b'\x0F\xaa', octets=13)
  'oXXXXXoXoXoXo'
  >>> bits2str(b'\x0F\xaa', octets=13, space=' ')
  'oXXXX XoXoXoXo'

  If pad bits are in the right side then they can be trimmed
  by setting from_left parameter to True.

  >>> bits2str(b'\x0F\xaa', octets=13, space='_',
  ...     from_left=True)
  'ooooXXXX_XoXoX'
  """
  if octets is None or octets == ...:
    octets = 8 * len(bytes_)
  if space is None:
    if octets % 8:
      space = ''
    else:
      space = ' '
  B_it = iter if from_left else reversed
  bits_params = (False, False) if from_left else (True, True)
  def char_gen():
    for i, b in enumerate(bits(bytes_, *bits_params), 1):
      if octets < i:
        break
      yield chars[b]
      if i < octets and not i % 8:
        yield space
  return ''.join(B_it(tuple(char_gen())))


def bytes2str(bytes_:bytes,
    space: str = ' ',
  ) -> str:
  """
  Convert a bytes object to string of hexadecimal values

  >>> bytes2str(b'hello world')
  '68 65 6C 6C 6F 20 77 6F 72 6C 64'

  Spaces between values can be turned of by setting the
  space parameter to an empty string.

  >>> bytes2str(b'hello world', space='')
  '68656C6C6F20776F726C64'

  Naturally, other space strings are possible.

  >>> bytes2str(b'hello world', space='_')
  '68_65_6C_6C_6F_20_77_6F_72_6C_64'
  """
  return space.join('{:0>2X}'.format(b) for b in bytes_)


def hexdigits_as_integers(stream: typing.io, *,
    octets: typing.Union[int, None, type(...)] = None,
    space: str = ' ',
    strict: bool = True,
  ) -> typing.Iterator[int]:
  """
  Yield integers by reading the stream for hexadecimal character
  pairs

  It is recommended to pass an explicit octets value if the
  length of the data in bytes is known beforehand. Note that
  octets = 8 * num_bytes and octets are calculated from the
  given parameter as octets = octets // 8 * 8.

  Note that the stream must be seekable and tellable.

  Spaces are ignored between byte values. The space parameter
  defines the space string (default ' ').

  >>> s = '68 65 6C 6C6F 2077 6 F 72 6C 64 '
  >>> stream = io.StringIO(s)
  >>> list(hexdigits_as_integers(stream, octets=11*8))
  [104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100]

  Strict mode is on by default. This means that
  * if octets then EOF expected after the required number of
    bytes were read;
  * if no octets then reading should go without invalid
    characters until EOF.

  >>> s += 'Hello World!'
  >>> stream = io.StringIO(s)
  >>> list(hexdigits_as_integers(stream))
  Traceback (most recent call last):
    ...
  ValueError: expected a hexdigit (0123456789abcdefABCDEF): 'H'
  >>> stream.read()
  '68 65 6C 6C6F 2077 6 F 72 6C 64 Hello World!'
  >>> stream.seek(0)
  0
  >>> list(hexdigits_as_integers(stream, strict=False))
  [104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100]
  >>> stream.read()
  ' Hello World!'
  """
  c, first_c = None, ''
  full_fb = fb = stream.tell()
  if octets == ...:
    octets = None
  octets = octets if octets is None else octets // 8 * 8
  while c != '' and (octets is None or -1 < octets):
    if not first_c and c != space:
      fb = stream.tell()
    c = stream.read(1)
    if c == space:
      continue
    if not c:
      if octets is not None and 0 < octets:
        stream.seek(full_fb)
        raise ValueError('EOF reached unexpectedly')
      continue  # exits the loop without break
    elif octets is not None and octets == 0:
      if strict and c:
        stream.seek(full_fb)
        raise ValueError('EOF expected')
      else:
        stream.seek(fb)
        break
    elif c not in string.hexdigits:
      if strict or (octets is not None and 0 < octets):
        exc_cls = ValueError
        stream.seek(full_fb)
      else:
        exc_cls = StopIteration
        stream.seek(fb)
      efs = 'expected a hexdigit ({}): {!r}'
      raise exc_cls(efs.format(string.hexdigits, c))
    elif not first_c:
      first_c = c
      continue
    else:
      yield int(first_c + c, 16)
      first_c = ''
      if octets is not None:
        octets -= 8
  else:
    if first_c:
      efs = 'last character without pair: {!r}'
      stream.seek(full_fb)
      raise ValueError(efs.format(first_c))


# TODO
def str2bits(s: typing.Union[str, typing.io], *,
    bitdigits: typing.Union[int, None] = None,
    from_left: bool = False,
    octets: typing.Union[int, None, type(...)] = None,
    space: str = ' ',
  ) -> bytes:
  """
  Convert a string of bitdigits to a bytes object or return a
  bytes object from a stream that has bitdigits in it.

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
  bitdigits parameter (default 'oX'). Note that matching is
  case sensitive.

  >>> str2bits('1_00001111_10101010', space='_', bitdigits='01')
  b'\x01\x0f\xaa'

  When called with a string, ValueError is raised if the string
  has invalid format. However, if the bitsize of the value is
  known beforehand then with an explicit octets parameter the
  reading could be stopped in time.

  >>> s = 'X ooooXXXX XoXoXoXo 3F 34'
  >>> str2bits(s)
  Traceback (most recent call last):
    ...
  ValueError: expected a bitdigit (oX): '3'
  >>> str2bits(s, octets=17)
  b'\x01\x0f\xaa'

  When called with a stream object then it gets consumed until
  it's format is valid and no exceptions are raised. Note that
  the stream must be seekable and tellable.

  >>> stream = io.StringIO(s)
  >>> str2bits(stream)
  b'\x01\x0f\xaa'
  >>> stream.read()
  ' 3F 34'
  """
  bitdigits = bitdigits or BITDIGITS
  if octets == ...:
    octets = None
  if not hasattr(s, 'read'):
    s = io.StringIO(s)
    exc_cls = ValueError
  else:
    exc_cls = None
  full_fb = s.tell()
  bools = list(bitdigits_as_booleans(s, bitdigits=bitdigits,
      exc_cls=exc_cls, octets=octets, space=space))
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
  if not hasattr(s, 'read'):
    s = io.StringIO(s)
    if strict is None:
      strict = True
  else:
    if strict is None:
      strict = False
  return bytes(x for x in hexdigits_as_integers(s,
      octets=octets, space=space, strict=strict))
