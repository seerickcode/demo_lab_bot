import functools
import threading

singleton_lock = threading.Lock()

def synchronized(singleton_lock):
    """ Sync Decorator """

    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kwargs):
            with singleton_lock:
                return f(*args, **kwargs)

        return inner_wrapper

    return wrapper


class Singleton(type):
    _instances = {}

    @synchronized(singleton_lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
