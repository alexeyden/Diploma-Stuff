import zmq
import sys


class IPC:
    SERVER = 0 # режим сервера
    CLIENT = 1 # режим клиента

    def __init__(self, path, mode = SERVER):
        self.context = zmq.Context()

        self.socket = self.context.socket(zmq.PAIR)

        if mode == IPC.SERVER:
            self.socket.bind('ipc://' + path)
        else:
            self.socket.connect('ipc://' + path)

        self.isOpen = True

    def send(self, data):
        self.socket.send_pyobj(data)

    def recv(self, timeout = 0):
        if timeout > 0:
            if self.socket.poll(timeout = timeout):
                return self.socket.recv_pyobj(flags = zmq.NOBLOCK)
            return None

        return self.socket.recv_pyobj()

    def close(self):
        self.socket.close()
        self.isOpen = False
