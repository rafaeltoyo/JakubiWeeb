# https://stackoverflow.com/questions/50566934/why-is-this-singleton-implementation-not-thread-safe

import threading
import functools


lock = threading.Lock()


def synchronized(lock):
    """ Synchronization decorator """
    def wrapper(f):
        @functools.wraps(f)
        def inner_wrapper(*args, **kw):
            with lock:
                return f(*args, **kw)
        return inner_wrapper
    return wrapper


class SingletonOld(type):
    """
    Singleton thread-safe
    https://stackoverflow.com/questions/48111037/concurrent-singleton-class-python
    FIXME: deadlock when call a singleton inside another singleton.__init__()
    """
    _instances = {}

    @synchronized(lock)
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonOld, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(type):
    """
    Singleton thread-safe (unstable version).
    https://stackoverflow.com/questions/48111037/concurrent-singleton-class-python
    https://gist.github.com/tkhoa2711/7ce18809febbca4828db
    https://eli.thegreenplace.net/2011/08/14/python-metaclasses-by-example/
    """
    _instances = {}
    _lock = threading.Lock()

    @synchronized(_lock)
    def __new__(mcs, name, bases, dct, *args, **kwargs):
        # Create class
        cls = super(Singleton, mcs).__new__(mcs, name, bases, dct)

        # Create class element in instances list.
        # instance will be create with __call__()
        # we'll create a lock for each class
        if cls not in Singleton._instances:
            Singleton._instances[cls] = {
                'instance': None,
                'lock': threading.Lock()
            }
        return cls

    def __call__(cls, *args, **kwargs):
        # Class element must be exist in list (created in __new__)
        cls_item = Singleton._instances[cls]

        # Check to avoid lock if instance already exist
        if cls_item["instance"] is None:

            # Thread protected area
            with cls_item["lock"]:

                # Double check because first check isn't thread safe
                if cls_item["instance"] is None:

                    cls_item["instance"] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls_item["instance"]
