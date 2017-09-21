from si.codec import enum as _enum_
from si.codec import integer as _integer_
from . import __product as _product_

# References:
# SPORTident.Communication/Communication.cs
#   0917311 (#L3023-3029)
ProductFamilyCodec = _enum_.EnumCodec.classfactory(
  'ProductFamilyCodec',
  enum=_product_.ProductFamily,
  subcodec=_integer_.Int8u,
)


codec = ProductFamilyCodec


del _product_
del _enum_
del _integer_
