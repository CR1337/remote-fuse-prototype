from machine import Pin, Timer
from state import state
import _thread
from time import sleep


class Fuse:

    PIN_IDS: list[int] = [18, 19, 20, 21]
    DURATION: int = 100  # ms

    _index: int
    _pin: Pin

    @property
    def pin(self) -> Pin:
        return self._pin

    def __init__(self, fuse_index: int):
        self._index = fuse_index
        self._pin = Pin(self.PIN_IDS[fuse_index], Pin.OUT)
        state.set_fuse_state_ready(fuse_index)

    def _unlight(self, timer: Timer):
        self._pin.value(0)
        timer.deinit()
        state.set_fuse_state_fired(self._index)

    def light(self) -> bool:
        if state.get_fuse_state(self._index) != 'ready':
            return False
        state.set_fuse_state_fireing(self._index)
        self._pin.value(1)
        Timer().init(
            mode=Timer.ONE_SHOT,
            period=self.DURATION,
            callback=self._unlight
        )
        return True


fuses = [Fuse(i) for i in range(state.fuse_amount)]


def _testloop_thread():
    PERIOD: float = 0.1
    for fuse in fuses:
        fuse.light()
        sleep(PERIOD)


def testloop():
    _thread.start_new_thread(_testloop_thread, ())
