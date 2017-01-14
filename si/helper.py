import functools

# http://stackoverflow.com/a/5192374/2334951
class classproperty:
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, owner):
        return self.f(owner)
