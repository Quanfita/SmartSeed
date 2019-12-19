import threading

class SingletonIns(object):
    __instance_lock = threading.Lock()

    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self, *args, **kw):
        if self._cls not in self._instance:
            with self.__instance_lock:
                if self._cls not in self._instance:
                    self._instance[self._cls] = self._cls(*args, **kw)
        return self._instance[self._cls]
