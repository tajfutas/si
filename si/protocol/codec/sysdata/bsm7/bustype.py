from si.protocol.codec import raw as _raw

# References:
# Communication.cs* 0917311 (#L3045-3073; #L3653-3883)
#     * named as cfg2
codec = _raw.RawCodec.classfactory('BusTypeCodec', bitsize=8)
