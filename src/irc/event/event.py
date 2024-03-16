class Event:
    def __init__(self):
        # make records of listeners by listener name
        self.listeners = {}

    def emit(self, name, data):
        if name in self.listeners:
            for listener in self.listeners[name]:
                listener.on(data)

    # on accepts string and function
    def on(self, listener, callback):
        if listener in self.listeners:
            self.listeners[listener].append(Listener(callback))
        else:
            self.listeners[listener] = []
            self.listeners[listener].append(Listener(callback))

    def remove(self, listener, callback):
        if listener in self.listeners:
            self.listeners[listener].remove(callback)


class Listener:
    def __init__(self, callback):
        self.callback = callback

    def on(self, data):
        self.callback(data)
