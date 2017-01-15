class Bytes(bytes):

  def __repr__(self):
    return '{}({})'.format(self.__class__.__name__,
        super().__repr__())

  def __str__(self):
    return ' '.join('{:0>2X}'.format(b) for b in self)

  @classmethod
  def from_str(cls, s: str) -> 'cls':
    """
    Create an instance from a string

    String must contain pairs of hexadecimal characters.
    Spaces and underscores are ignored.
    """
    def pair_gen():
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
    return cls(x for x in pair_gen())
