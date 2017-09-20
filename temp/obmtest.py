from si.utils import obm

class Test(obm.base.Base):
  c : obm.types.Integer(0o20, default=10)
  a : obm.types.Integer(0o40, True, readonly=True)
  b : obm.types.Integer(0o40, False)

x = obm.types.Integer(0o10, True)

t = Test()

t.a=1
t.b=2
