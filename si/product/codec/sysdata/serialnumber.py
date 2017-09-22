from si.codec import integer as _integer_

# References:
# Communication.cs 0917311 (#L3034-3044)
SerialNumberCodec = _integer_.Int32ub


codec = SerialNumberCodec


del _integer_
