from led import led
from network_ import Network


def main():
    led.blink_long()
    Network.connect()
    webserver = Network.create_webserver()
    led.blink_short()
    webserver.run()


main()
