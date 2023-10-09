from led import led
from fuse import fuses


def panic():
    print("PANIC")
    led.on()
    for fuse in fuses:
        fuse.pin.value(0)
    raise RuntimeError("PANIC")
