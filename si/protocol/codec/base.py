from functools import wraps as _wraps

from si.utils.funcdeco import doublewrap as _doublewrap


#@_doublewrap
def encodemethod(m, mask=None):
  @_wraps(m)
  def wrapped(cls, obj, data=None, data_idxs=None):
    enc_data = m(cls, obj)
    if data is None:
      return enc_data
    else:
      if data_idxs is None:
        data_idxs = range(len(data))
      assert len(enc_data) == len(data_idxs)
      if isinstance(mask, int) and len(data_idxs) == 1:
        mask_ = (mask,)
      elif mask is not None:
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


class BaseCodec:

  @classmethod
  def decode(cls, data):
    ...

  @classmethod
  @encodemethod
  def encode(cls, obj):
    ...

  @classmethod
  def classfactory(cls, name, *, bases=None, **dict_):
    bases = ((cls,) if bases is None else bases)
    return type(name, bases, dict_)
