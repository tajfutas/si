import typing


class Rollbackable:
  """
  Wraps an iterable and makes it rollbackable by caching its
  values.
  """

  _cache_type = list

  def __init__(self,
      subiterable: typing.Iterable,
    ):
    self._cache = self._cache_type()
    self._cache_index = 0
    if hasattr(subiterable, '__next__'):
      self._subiterable = subiterable
    else:
      self._subiterable = iter(subiterable)

  def __iter__(self):
    return self

  def __next__(self):
    cached_behind = self.cached_behind
    cached = self.cached
    if cached_behind == cached:
      val = next(self._subiterable)
      self._append_to_cache(val)
    elif cached_behind < cached:
      val = self._cache[cached_behind]
    else:
      raise RuntimeError('invalid cachce index')
    self._cache_index += 1
    return val

  @property
  def cached(self):
    "Length of the cache."
    return len(self._cache)

  @property
  def cached_ahead(self):
    """
    Length of the cache ahead current position.

    If it equals zero then the next value will be taken from
    the wrapped iterable.
    """
    return self.cached - self.cached_behind

  @property
  def cached_behind(self):
    """
    Length of the cache behind current position.

    If equals cached then the next value will be taken from
    the wrapped iterable.
    """
    return self._cache_index

  def _append_to_cache(self, val):
    self._cache.append(val)

  def _extend_cache_with(self, vals):
    self._cache.extend(val for val in vals)

  def cache_purge_ahead(self,
      size: typing.Union[None, int] = None,
    ):
    """
    Purges cache values ahead of current position.

    If size is None or omitted then it purges all values.
    """
    if size is None:
      size = self.cached_ahead
    elif not (0 <= size <= self.cached_ahead):
      raise ValueError('expected 0 <= size <= cached_ahead')
    if 0 < size:
      cached_behind = self.cached_behind
      self._cache = (self._cache[:cached_behind]
          + self._cache[cached_behind + size:])

  def cache_purge_behind(self,
      size: typing.Union[None, int] = None,
    ):
    """
    Purges cache values behind of current position.

    If size is None or omitted then it purges all values.
    """
    if size is None:
      size = self.cached_behind
    elif not (0 <= size <= self.cached_behind):
      raise ValueError('expected 0 <= size <= cached_behind')
    if 0 < size:
      self._cache = self._cache[size:]
      self._cache_index -= size

  def rollahead(self,
      size: typing.Union[None, int] = None,
    ):
    """
    Rollahead values which will be skipped.

    If size is 1 then the one value of the ahead cache is going
    to be skipped from being yielded.
    If size is None then all values of the ahead cache are going
    to be skipped.
    """
    if size is None:
      self._cache_index = self.cached
    elif not (0 <= size <= self.cached_ahead):
      raise ValueError('expected 0 <= size <= cached_ahead')
    else:
      self._cache_index += size

  def rollback(self,
      size: typing.Union[None, int] = None,
    ):
    """
    Rollback values which will be yielded again if not purged.

    If size is 1 then the last value is going to be repeated.
    If size is None then rolls back to the first value of the
    cache.
    """
    if size is None:
      self._cache_index = 0
    elif not (0 <= size <= self.cached_behind):
      raise ValueError('expected 0 <= size <= cached_behind')
    else:
      self._cache_index -= size


class RollbackableBytesMixin:

  _cache_type = bytearray

  def _append_to_cache(self, val):
    try:
      super()._append_to_cache(val)  # int
    except TypeError:
      self._extend_cache_with(val)  # bytes

  def __next__(self):
    from_subiterable = (self.cached_behind == self.cached)
    next_obj = super().__next__()
    try:
      return next_obj[0]  # bytes --> int
    except TypeError:
      return next_obj  # int


class RollbackableReadMixin:

  def __init__(self,
      io: typing.io,
    ):
    self._io = io
    super().__init__(self._reader())

  @property
  def io(self):
      return self._io

  def _reader(self):
    while True:
      val = self._io.read(1)
      if not val:
        raise StopIteration()
      else:
        yield val

  def readinto(self,
      size: typing.Union[None, int] = None,
    ):
    """
    Read into cache.

    Returns number of objects read (0 for EOF).
    """
    vals = self._io.read(size)
    self._extend_cache_with(vals)
    return len(vals)


class RollbackableBytes(
    RollbackableBytesMixin,
    Rollbackable,
  ):
  """
  Wraps an iterable of bytes objects (or integers in range
  0--255) and makes it rollbackable by caching its values as
  integers.

  Note that the resulted iterator yields integers.
  """


class RollbackableRead(
    RollbackableReadMixin,
    Rollbackable,
  ):
  """
  Iterator which makes the read of a stream rollbackable.
  Reading is wrapped by the iterator and that API (for; next)
  should be used for reading from the stream.

  Note that only read is wrapped; write must be done separately.
  """


class RollbackableBytesRead(
    RollbackableBytesMixin,
    RollbackableReadMixin,
    Rollbackable,
  ):
  """
  Iterator which makes the read of a bytes stream rollbackable.
  Reading is wrapped by the iterator and that API (for; next)
  should be used for reading from the stream.

  Note that the resulted iterator yields integers and only read
  is wrapped; write must be done separately.
  """

def rollbackable(
    obj: typing.Union[
        typing.Iterable[typing.Union[bytes, str]],
        typing.io,
      ]
  ) -> Rollbackable:
  """
  Factory function to wrap a string or bytes object, or a stream
  object of those types to a Rollbackable object.
  """
  if hasattr(obj, 'read'):
    if not hasattr(obj, 'encoding'):
      return RollbackableBytesRead(obj)
    else:
      return RollbackableRead(obj)
  elif hasattr(obj, 'decode'):
    return RollbackableBytes(obj)
  else:
    return Rollbackable(obj)


del typing
