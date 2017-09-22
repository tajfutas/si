from si.codec import integer as _integer_


# References:
# Communication.cs* 0917311 (#L3045-3073; #L3653-3883)
#     * named as cfg2
BusTypeCodec = _integer_.Int8u


codec = BusTypeCodec


del _integer_
