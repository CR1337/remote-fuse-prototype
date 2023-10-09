import network
import socket
import time
import json
from panic import panic
from webserver import Webserver


class Network:

    WAIT_TIME: float = 1.0  # s
    WAIT_AMOUNT: int = 10
    PORT: int = 8080

    _wlan: network.WLAN = network.WLAN(network.STA_IF)
    _socket: socket.socket

    @classmethod
    def connect(cls):
        cls._wlan.active(True)
        with open("wlan.json", 'r') as file:
            credentials = json.load(file)
        cls._wlan.connect(credentials['ssid'], credentials['password'])

        for _ in range(cls.WAIT_AMOUNT):
            print('waiting for connection...')
            if cls._wlan.status() < 0 or cls._wlan.status() >= 3:
                break
            time.sleep(cls.WAIT_TIME)
        else:
            print("network connection failed")
            panic()

    @classmethod
    def _open_socket(cls) -> socket.socket:
        address = socket.getaddrinfo('0.0.0.0', cls.PORT)[0][-1]
        socket_ = socket.socket()
        socket_.bind(address)
        socket_.listen()
        print('listening on', address)
        return socket_

    @classmethod
    def create_webserver(cls) -> Webserver:
        socket_ = cls._open_socket()
        return Webserver(socket_)
