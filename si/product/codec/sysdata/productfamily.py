from si.codec import Codec as _Codec_
from si.codec import MaskedIndexedData as _MaskedIndexedData_
from si.codec import enum as _enum_
from si.codec import integer as _integer_
from si.product import ProductFamily as _ProductFamily_

# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3023-3029)
class ProductFamilyCodec(_Codec_):

  bitsize = 8
  subcodec = _enum_.EnumCodec.classfactory(
      'ProductFamilySubCodec',
      enum=_ProductFamily_,
      subcodec=_integer_.Int8u,
  )

  @classmethod
  @_Codec_.decodemethod
  def decode(cls, data, idxmap):
    value = data[idxmap['CFG0']]
    return cls.subcodec.decode([value])

  @classmethod
  @_Codec_.encodemethod(pass_data=True)
  def encode(cls, value, data, idxmap):
    mask = b'\xFF'
    idxs = (idxmap['CFG0'],)
    enc_data  = cls.subcodec.encode(value)
    return _MaskedIndexedData_(enc_data, idxs, mask)
  #keep _MaskedIndexedData_


codec = ProductFamilyCodec


del _Codec_
del _enum_
del _integer_
del _ProductFamily_
