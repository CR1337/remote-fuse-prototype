from machine import Pin
import json


class State:

    DIP_PINS_IDS: list[int] = [0, 1, 2, 3, 4, 5, 6, 7]
    ADDRESS_BIT_INDICES: list[int] = [0, 1, 2, 3, 4, 5]
    FUSE_AMOUNT_BIT_INDICES: list[int] = [6, 7]

    DEVICE_IDS_FILENAME: str = "device_ids.json"
    DEVICE_IDS: list[str]
    with open(DEVICE_IDS_FILENAME, 'r') as file:
        DEVICE_IDS = json.load(file)

    _dip_pins: list[Pin]
    _remote_device_index: int

    _device_id: str
    _fuse_amount: int
    _fuse_states: list[str]

    def __init__(self):
        self._dip_pins = [
            Pin(pin_id, Pin.IN)
            for pin_id in self.DIP_PINS_IDS
        ]
        self._read_remote_device_index()
        self._device_id = self.DEVICE_IDS[self._remote_device_index]
        self._read_fuse_amount()
        self._fuse_states = ["ready"] * self._fuse_amount

    def _read_remote_device_index(self):
        self._remote_device_index = 0
        for i, bit_index in enumerate(reversed(self.ADDRESS_BIT_INDICES)):
            pin = self._dip_pins[bit_index]
            self._remote_device_index += pin.value() * 2 ** i

    def _read_fuse_amount(self):
        self._fuse_amount = 1
        for i, bit_index in enumerate(reversed(self.FUSE_AMOUNT_BIT_INDICES)):
            pin = self._dip_pins[bit_index]
            self._fuse_amount += pin.value() * 2 ** i

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def fuse_amount(self) -> int:
        return self._fuse_amount

    def set_fuse_state_ready(self, fuse_index: int):
        self._fuse_states[fuse_index] = "ready"

    def set_fuse_state_fireing(self, fuse_index: int):
        self._fuse_states[fuse_index] = "fireing"

    def set_fuse_state_fired(self, fuse_index: int):
        self._fuse_states[fuse_index] = "fired"

    def get_fuse_state(self, fuse_index: int) -> str:
        return self._fuse_states[fuse_index]

    def __str__(self) -> str:
        return json.dumps({
            'fuse_amount': self._fuse_amount,  # type: ignore
            'device_id': self._device_id,  # type: ignore
            'fuse_states': self._fuse_states  # type: ignore
        })

    def update_device_ids(self, device_ids: list[str]):
        with open(self.DEVICE_IDS_FILENAME, 'w') as file:
            json.dump(device_ids, file)


state = State()
