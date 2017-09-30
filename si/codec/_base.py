import collections as _collections_
import functools as _functools_
import inspect as _inspect_


# encodemethods should return this type to make data
# dynamically masked
IndexedData = _collections_.namedtuple(
    'IndexedData',
    ('data', 'data_idxs'),
)
MaskedData = _collections_.namedtuple(
    'MaskedData',
    ('data', 'mask'),
)
MaskedIndexedData = _collections_.namedtuple(
    'MaskedIndexedData',
    ('data', 'data_idxs', 'mask'),
)


def _decodemethod(m):
  @_functools_.wraps(m)
  def wrapped(cls, data, *args, data_idxs=None, **kwargs):
    mask = (cls.mask if hasattr(cls, 'mask') else None)
    try:
      arg_i = _inspect_.getargspec(m).args.index('data_idxs')
    except ValueError:
      pass
    else:
      arg_i -= 2  # cls, data
      if arg_i < len(args):
        data_idxs = args[arg_i]
        args = args[:arg_i] + args[arg_i + 1:]
    if hasattr(data_idxs, '__members__'):
      kwargs['data_idxs'] = data_idxs
    else:
      s = _inspect_.signature(m)
      if 'data_idxs' in s.parameters:
        kwargs['data_idxs'] = data_idxs
    if mask is None:
      data_ = bytearray(data)
    if data_idxs is None or hasattr(data_idxs, '__members__'):
      data_ = bytearray(data)
    else:
      data_ = bytearray(data[i] for i in data_idxs)
    if mask is not None:
      len_ = len(data_)
      if isinstance(mask, int):
        mask = (mask,)
      assert len(mask) == len_
      for i, b in enumerate(data_):
        mask_v = mask[i]
        data_[i] = b & mask_v
    obj = m(cls, data_, *args, **kwargs)
    return obj
  return wrapped
#keep _functools_


def _encodemethod(m):
  @_functools_.wraps(m)
  def wrapped(cls, *args, data=None, data_idxs=None,
        **kwargs):
    mask = (cls.mask if hasattr(cls, 'mask') else None)
    s = _inspect_.signature(m)
    if 'data' in s.parameters:
      kwargs['data'] = data
    if 'data_idxs' in s.parameters:
      kwargs['data_idxs'] = data_idxs
    m_result = m(cls, *args, **kwargs)
    if hasattr(m_result, 'data'):
      enc_data = m_result.data
    else:
      enc_data = m_result
    if hasattr(m_result, 'mask'):
      mask = m_result.mask
    if hasattr(m_result, 'data_idxs'):
      data_idxs = m_result.data_idxs
    if mask is None and data is None:
      return enc_data
    if data_idxs is None:
      data_idxs_ = range(len(enc_data))
    else:
      data_idxs_ = data_idxs
    len_ = len(data_idxs_)
    if mask is not None:
      if isinstance(mask, int):
        mask = (mask,)
      assert len(mask) == len_
    if data is None:
      data_ = bytearray(len_)
    else:
      data_ = data
    for enc_i, dat_i in enumerate(data_idxs_):
      if mask is None:
        data_[dat_i] = enc_data[enc_i]
      else:
        mask_v = mask[enc_i]
        inv_mask_v = 255 - mask_v
        masked_enc_data = enc_data[enc_i] & mask_v
        if data is None:
          data_[dat_i] = masked_enc_data
        else:
          masked_data = data[dat_i] & inv_mask_v
          data_[dat_i] = masked_data + masked_enc_data
    if data is None:
      return bytes(data_)
    else:
      return data
  return wrapped
#keep _inspect_


class Codec:

  bitsize = ...

  decodemethod = _decodemethod
  encodemethod = _encodemethod

  @classmethod
  @decodemethod
  def decode(cls, data):
    raise NotImplementedError(
        'decode() classmethod should be defined in every Codec '
        'subclasses decorated with @decodemethod'
      )

  @classmethod
  @encodemethod
  def encode(cls, obj):
    raise NotImplementedError(
        'encode() classmethod should be defined in every Codec '
        'subclasses decorated with @encodemethod'
      )

  @classmethod
  def classfactory(cls, name, *, bases=None, **dict_):
    bases = ((cls,) if bases is None else bases)
    return type(name, bases, dict_)


del _collections_
