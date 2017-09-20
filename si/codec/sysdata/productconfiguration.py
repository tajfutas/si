from si.codec import integer as _integer_


# References:
# Communication.cs 0917311 (#L3023-3029)
ProductConfigurationCodec = _integer_.Int16ub


codec = ProductConfigurationCodec


del _integer_
