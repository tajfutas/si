import functools

# http://stackoverflow.com/a/5192374/2334951
class classproperty:
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, owner):
        return self.f(owner)


# http://www.dabeaz.com/coroutines/coroutine.py
# http://stackoverflow.com/a/1073582/2334951
def coroutine(func):
    @functools.wraps(func)
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        next(cr)
        return cr
    return start
