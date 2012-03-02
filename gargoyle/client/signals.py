class Signal(object):

    def __init__(self):
        self.__callbacks = []

    def connect(self, callback):
        if not callable(callback):
            raise ValueError("Callback argument must be callable")

        self.__callbacks.append(callback)

    def call(self, *args, **kwargs):
        for callback in self.__callbacks:
            callback(*args, **kwargs)

    def reset(self):
        self.__callbacks = []


switch_registered = Signal()
switch_unregistered = Signal()
switch_updated = Signal()
condition_apply_error = Signal()
switch_checked = Signal()
switch_active = Signal()
