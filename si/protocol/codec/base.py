from functools import wraps as _wraps


def decodemethod(m):
  @_wraps(m)
  def wrapped(cls, data, *args, data_idxs=None, **kwargs):
    mask = (cls.mask if hasattr(cls, 'mask') else None)
    if mask is None and data_idxs is None:
      data_ = data
    if data_idxs is None:
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


def encodemethod(m):
  @_wraps(m)
  def wrapped(cls, *args, data=None, data_idxs=None,
        **kwargs):
    enc_data = m(cls, *args, **kwargs)
    mask = (cls.mask if hasattr(cls, 'mask') else None)
    if mask is None and data is None:
      return enc_data
    if data_idxs is None:
      data_idxs = range(len(enc_data))
    len_ = len(data_idxs)
    if mask is not None:
      if isinstance(mask, int):
        mask = (mask,)
      assert len(mask) == len_
    if data is None:
      data_ = bytearray(len_)
    else:
      data_ = data
    for enc_i, dat_i in enumerate(data_idxs):
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
