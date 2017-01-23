import collections
import io
import string
import typing


def bits2str(bytes_: bytes,
    octets: typing.Union[int, None] = None,
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
  if octets is None:
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



def bits(bytes_: bytes,
    reversed_bytes: bool = False,
    reversed_bits: bool = False
  ) -> typing.Iterator[int]:
  """
  Yield bits of the given bytes object

  >>> list(iterbits(b'\x0F\xAA'))
  [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0]
  >>> list(iterbits(b'\x0F\xAA', reversed_bytes=True))
  [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1]
  >>> list(iterbits(b'\x0F\xAA', reversed_bits=True))
  [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1]
  >>> list(iterbits(b'\x0F\xAA', reversed_bytes=True,
  ...     reversed_bits=True))
  [0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0]

  """
  B_it = reversed if reversed_bytes else iter
  b_it = iter if reversed_bits else reversed
  yield from ((B & 2**i) >> i for B in B_it(bytes_)
      for i in b_it(range(8)))


def hexdigits_as_integers(stream: typing.io,
    space: str = ' ',
    exc_cls: typing.Union[None, typing.Type[Exception]] = None,
  ) -> typing.Iterator[str]:
  """
  Yield integers by reading the stream for hexadecimal character
  pairs

  Spaces are ignored between byte values. The space parameter
  defines the space string (default ' ').

  >>> s = '68 65 6C 6C6F 2077 6 F 72 6C 64 whatever'
  >>> stream = io.StringIO(s)
  >>> gen = hexdigits_as_integers(stream)
  >>> li = list(gen)
  [104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100]
  >>> bytes(li)
  b'hello world'
  >>> stream.read()
  ' whatever'

  By default the iteration stops at invalid characters without
  raising an exception. This can be overridden with an explicit
  exc_cls (exception class) parameter (defalut StopIteration).

  >>> stream.seek(0)
  0
  >>> gen = hexdigits_as_integers(stream, exc_cls=ValueError)
  >>> li = list(gen)
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "C:\tajf\si\si\protocol\_helper.py", line 162, in
        hexdigits_as_integers
      raise exc_cls(efs.format(c))
  ValueError: expected a hexdigit: 'w'
  >>> stream.read()
  '68 65 6C 6C6F 2077 6F 72 6C 64 whatever'
  """
  exc_cls = StopIteration if exc_cls is None else exc_cls
  c, first_c = None, ''
  full_fb = fb = stream.tell()
  while c != '':
    if not first_c and c != space:
      fb = stream.tell()
    c = stream.read(1)
    if not c:
      continue
    if c == space:
      continue
    elif c not in string.hexdigits:
      stream.seek((fb if exc_cls == StopIteration else full_fb))
      efs = 'expected a hexdigit: {!r}'
      raise exc_cls(efs.format(c))
    elif not first_c:
      first_c = c
      continue
    else:
      yield int(first_c + c, 16)
      first_c = ''
  else:
    if first_c:
      efs = ('last character without pair: {!r}')
      stream.seek((fb if exc_cls == StopIteration else full_fb))
      raise exc_cls(efs.format(first_c))


def str2bits(s: str,
    octets: typing.Union[int, None] = None,
    space: str = None,
    chars: typing.Sequence[str] = 'oX',
    from_left: bool = False,
  ) -> typing.Iterator[int]:
  pass
  # TODO

def str2bytes(s: typing.Union[str, typing.io],
    space: str = ' ',
  ) -> bytes:
  """
  Convert a string of hexadecimal vales to a bytes object
  or return a bytes object from a stream that has hexadecimal
  characters in it

  >>> s = '68 65 6C 6C 6F 20 77 6F 72 6C 64'
  >>> si.protocol._base.str2bytes(s)
  b'hello world'

  Spaces are ignored between byte values. The space parameter
  defines the space string (default ' ').

  >>> s2 = s.replace(' ', '_')
  >>> s2
  '68_65_6C_6C_6F_20_77_6F_72_6C_64'
  >>> si.protocol._base.str2bytes(s2, space='_')
  b'hello world'
  """
  if not hasattr(s, 'read'):
    s = io.StringIO(s)
    exc_cls = ValueError
  else:
    exc_cls = None
  return bytes(x for x in hexdigits_as_integers(s, space=space,
      exc_cls=exc_cls))

