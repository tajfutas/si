from functools import wraps as _wraps

from si.utils.funcdeco import doublewrap as _doublewrap


@_doublewrap
def decodemethod(m, mask=None):
  @_wraps(m)
  def wrapped(cls, data, *args, data_idxs=None, **kwargs):
    if data_idxs is None:
      data_ = bytearray(data)
    else:
      data_ = bytearray(data[i] for i in data_idxs)
    if mask is not None:
      if len(data_idxs) == 1 and isinstance(mask, int):
        mask_ = (mask,)
      else:
        assert len(mask) == len(data_)
        mask_ = mask
      for i, b in enumerate(data_):
        mask_v = mask_[i]
        data_[i] = b & mask_v
    obj = m(cls, data_, *args, **kwargs)
    return obj
  return wrapped


@_doublewrap
def encodemethod(m, mask=None):
  @_wraps(m)
  def wrapped(cls, *args, data=None, data_idxs=None,
        **kwargs):
    enc_data = m(cls, *args, **kwargs)
    if data is None:
      return enc_data
    else:
      if data_idxs is None:
        data_idxs = range(len(data))
      assert len(enc_data) == len(data_idxs)
      if mask is not None:
        if len(data_idxs) == 1 and isinstance(mask, int):
          mask_ = (mask,)
        else:
          assert len(mask) == len(data_idxs)
          mask_ = mask
      for enc_i, dat_i in enumerate(data_idxs):
        if mask is None:
          data[dat_i] = enc_data[enc_i]
        else:
          mask_v = mask_[i]
          inv_mask_v = 255 - mask_v
          masked_data = data[dat_i] & inv_mask_v
          masked_enc_data = enc_data[enc_i] & mask_v
          data[dat_i] = masked_data + masked_enc_data
      return data
  return wrapped


class Codec:

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


del _doublewrap
