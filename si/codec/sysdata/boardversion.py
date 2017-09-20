from si.codec import integer as _integer_


BoardVersionCodec = _integer_.Int8u.classfactory(
  'BoardVersionCodec',
  mask=0b00001111,
)


codec = BoardVersionCodec


del _integer_
