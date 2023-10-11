from state import state
from fuse import fuses, testloop
import json


class Endpoints:

    OK_200: int = 200
    BAD_REQUEST_400: int = 400
    NOT_FOUND_404: int = 404

    @classmethod
    def index(cls) -> tuple[str, int]:
        return f"This is remote fuse '{state.device_id}'.", cls.OK_200

    @classmethod
    def discover(cls) -> tuple[str, int]:
        return (
            json.dumps({
                'device_id': state.device_id,  # type: ignore
                'is_remote': True  # type: ignore
            }),
            cls.OK_200
        )

    @classmethod
    def fire(cls, index: int) -> tuple[str, int]:
        if index < 0 or index >= len(fuses):
            return cls.not_found()
        if fuses[index].light():
            return cls.ok()
        else:
            return cls.bad_request()

    @classmethod
    def testloop(cls) -> tuple[str, int]:
        testloop()
        return cls.ok()

    @classmethod
    def state(cls) -> tuple[str, int]:
        return str(state), cls.OK_200

    @classmethod
    def update_device_ids(cls, device_ids: list[str]) -> tuple[str, int]:
        state.update_device_ids(device_ids)
        return cls.ok()

    @classmethod
    def not_found(cls) -> tuple[str, int]:
        return "{}", cls.NOT_FOUND_404

    @classmethod
    def bad_request(cls) -> tuple[str, int]:
        return "{}", cls.BAD_REQUEST_400

    @classmethod
    def ok(cls) -> tuple[str, int]:
        return "{}", cls.OK_200
