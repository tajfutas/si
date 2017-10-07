import collections as _collections_
import functools as _functools_
import inspect as _inspect_

from si.utils.funcdeco import doublewrap as _doublewrap_


# encodemethods should return this type to make data
# dynamically masked
IndexedData = _collections_.namedtuple(
    'IndexedData',
    ('data', 'idxs'),
)
MaskedData = _collections_.namedtuple(
    'MaskedData',
    ('data', 'mask'),
)
MaskedIndexedData = _collections_.namedtuple(
    'MaskedIndexedData',
    ('data', 'idxs', 'mask'),
)


def _ensure_nice_args(
      argspec, args, kwargs,
      passargs, passdict,
  ):
  missing_args = [
      a for a in argspec.args
      if a not in ('cls', 'self') and a not in kwargs
  ]
  missing_args = missing_args[len(args):]
  if missing_args:
    args = list(args)
  for arg in missing_args:
    if arg not in passargs:
      continue
    args.append(passargs[arg])
    passdict[arg] = False
  for arg in (arg for arg in passdict if passdict[arg]):
    kwargs[arg] = passargs[arg]
  return args, kwargs

@_doublewrap_
def _decodemethod(m, *, pass_idxs=False):
  argspec = _inspect_.getfullargspec(m)
  @_functools_.wraps(m)
  def wrapped(cls, data, *args, idxs=None, **kwargs):
    mask = (cls.mask if hasattr(cls, 'mask') else None)
    passargs = {'idxs': idxs}
    passdict = {'idxs': pass_idxs}
    args, kwargs = _ensure_nice_args(
        argspec, args, kwargs, passargs, passdict
    )
    if mask is None or idxs is None:
      data_ = bytearray(data)
    else:
      data_ = bytearray(data[i] for i in idxs)
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


@_doublewrap_
def _encodemethod(m, *, pass_data=False, pass_idxs=False):
  argspec = _inspect_.getfullargspec(m)
  @_functools_.wraps(m)
  def wrapped(cls, *args, data=None, idxs=None,
        **kwargs):
    pass_data_, pass_idxs_ = pass_data, pass_idxs
    mask = (cls.mask if hasattr(cls, 'mask') else None)
    passargs = {'data': data, 'idxs': idxs}
    passdict = {'data': pass_data, 'idxs': pass_idxs}
    args, kwargs = _ensure_nice_args(
        argspec, args, kwargs, passargs, passdict
    )
    m_result = m(cls, *args, **kwargs)
    if hasattr(m_result, 'data'):
      enc_data = m_result.data
    else:
      enc_data = m_result
    if hasattr(m_result, 'mask'):
      mask = m_result.mask
    if hasattr(m_result, 'idxs'):
      idxs = m_result.idxs
    if mask is None and data is None:
      return enc_data
    if idxs is None:
      idxs_ = range(len(enc_data))
    else:
      idxs_ = idxs
    len_ = len(idxs_)
    if mask is not None:
      if isinstance(mask, int):
        mask = (mask,)
      assert len(mask) == len_
    if data is None:
      data_ = bytearray(len_)
    else:
      data_ = data
    for enc_i, dat_i in enumerate(idxs_):
      if mask is None:
        data_[dat_i] = enc_data[enc_i]
      else:
        mask_v = mask[enc_i]
        if not mask_v:
          continue
        elif mask_v == 255:
          data_[dat_i] = enc_data[enc_i]
        else:
          inv_mask_v = 255 - mask_v
          masked_enc_data = enc_data[enc_i] & mask_v
          if data is None:
            data_[dat_i] = masked_enc_data
          else:
            masked_data = data[dat_i] & inv_mask_v
            data_[dat_i] = masked_data + masked_enc_data
    return enc_data
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
del _doublewrap_
