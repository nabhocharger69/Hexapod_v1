from PySide6.QtCore import QObject, Signal, Slot
import socket


class BluetoothClient(QObject):
    status = Signal(int, object)
    message = Signal(object, object)
    ERROR = -1
    LISTEN = 1
    CONNECTED = 2
    STOP = 3

    SIG_NORMAL = 0
    SIG_STOP = 1
    SIG_DISCONNECT = 2

    def __init__(self, mac, port):
        QObject.__init__(self)

        self.mac = mac
        self.port = port
        self.bt_socket = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.bt_socket.settimeout(1)

        self.signal = self.SIG_NORMAL

    @Slot()
    def start(self):
        try:
            self.bt_socket.connect((self.mac, self.port))
        except OSError as err:
            print(err)
            # self.status.emit(self.STOP, '')
        else:
            # print('connected')
            self.status.emit(self.CONNECTED, self.mac)

            while True:
                if self.signal == self.SIG_NORMAL:
                    try:

                        data = self.bt_socket.recv(4096)
                    except socket.timeout as t_out:
                        pass
                    else:
                        if data:
                            self.message.emit(
                                self.mac+' ('+str(self.port)+')',
                                data.decode())
                        else:
                            break
                elif self.signal == self.SIG_DISCONNECT:
                    self.signal = self.SIG_NORMAL
                    self.bt_socket.close()
                    break
        finally:
            self.status.emit(self.STOP, '')

    def send(self, msg):
        self.bt_socket.sendall(msg.encode())

    def close(self):
        self.signal = self.SIG_DISCONNECT
