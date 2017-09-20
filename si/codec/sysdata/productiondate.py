from si.codec import time as _time_


# References:
# Communication.cs 0917311 (#L3006-3022)
ProductionDateCodec = _time_.DateCodec


codec = ProductionDateCodec


del _time_
