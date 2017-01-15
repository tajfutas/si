class BaseBytes(bytes):

  def __repr__(self):
    return '{}({})'.format(self.__class__.__name__,
        super().__repr__())


class Bytes(BaseBytes):

  def __str__(self):
    return ' '.join('{:0>2X}'.format(b) for b in self)

  @classmethod
  def from_str(cls, s: str) -> 'cls':
    """
    Create an instance from a string

    String must contain pairs of hexadecimal characters.
    Spaces and underscores are ignored.
    """
    def intgen():
      first_c = ''
      for c in s:
        if c in ' _':
          continue
        elif not first_c:
          first_c = c
          continue
        else:
          yield int(first_c + c, 16)
          first_c = ''
      else:
        if first_c:
          efs = ('expected a pair of hexadecimal characters '
              'instead of: {!r}')
          raise ValueError(efs.format(first_c))
    return cls(x for x in intgen())


class Bits(BaseBytes):

  def __str__(self):
    def char_gen(spaces):
      for i, B in enumerate(self):
        for c in '{:0>8b}'.format(B):
          yield ('X' if c == '1' else 'o')
        if spaces and i + 1 < len(self):
          yield ' '
    if hasattr(self, '_bits'):
      return ''.join(char_gen(False))[-self.num_bits:]
    else:
      return ''.join(char_gen(True))

  @classmethod
  def from_str(cls, s: str) -> 'cls':
    """
    Create an instance from a string

    String must contain case insensitive "o", "0", "X", and "1"
    characters only. Spaces and underscores are ignored.
    """
    def reversed_intgen():
      bit_vals = []
      for c in reversed(s.lower()):
        if c in ' _':
          continue
        if c in 'o0':
          bit_vals.append(0)
        elif c in 'x1':
          bit_vals.append(2**len(bit_vals))
        else:
          efs = ('expected "o", "0", "X", and "1" characters '
              'instead of: {!r}')
          raise ValueError(efs.format(c))
        if len(bit_vals) == 8:
          yield sum(bit_vals)
          bit_vals = []
      else:
        if bit_vals:
          yield sum(bit_vals)
    return cls(x for x in reversed(list(reversed_intgen())))
