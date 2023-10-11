import socket
from endpoints import Endpoints
from panic import panic
from led import led


class Webserver:

    STATUS_STRING: dict[int, str] = {
        200: "OK",  # type: ignore
        400: "BAD REQUEST",  # type: ignore
        404: "NOT FOUND"  # type: ignore
    }

    _socket: socket.socket
    _current_connection: socket.socket
    _shutdown: bool

    def __init__(self, socket_: socket.socket):
        self._socket = socket_
        self._shutdown = False

    def run(self):
        while not self._shutdown:
            try:
                self._mainloop()
            except Exception as ex:
                print(ex)
                self._current_connection.close()
                print('connection closed')
                panic()
        led.off()

    def _extract_parameters(
        self, parameter_string: str
    ) -> dict[str, str] | None:
        if parameter_string == "":
            return None
        parameters = parameter_string.split("&")
        result = {}
        for parameter in parameters:
            if "=" not in parameter:
                return None
            key, value = parameter.split("=")
            result[key] = value
        return result

    def _extract_fuse_index(self, parameter_string: str) -> int | None:
        parameters = self._extract_parameters(parameter_string)
        if parameters is None:
            return None
        if 'index' in parameters:  # type: ignore
            try:
                return int(parameters['index'])  # type: ignore
            except ValueError:
                return None
        return None

    def _extract_device_ids(self, parameter_string) -> list[str] | None:
        parameters = self._extract_parameters(parameter_string)
        if parameters is None:
            return None
        if 'device-ids' in parameters:  # type: ignore
            value = parameters['device-ids']
            if not value.startswith("[") or not value.endswith("]"):
                return None
            return value[1:-1].split(",")
        return None

    def _mainloop(self):
        self._current_connection, address = self._socket.accept()
        request = str(self._current_connection.recv(1024))
        url = request.split(" ")[1]
        parameter_string = url.split("?")[-1] if "?" in url else ""
        location = url.split("?")[0] if "?" in url else url
        content_type = "application/json"

        if location == "/":
            content, status = Endpoints.index()
            content_type = "text/html"
        elif location == "/discover":
            content, status = Endpoints.discover()
        elif location == "/fire":
            fuse_index = self._extract_fuse_index(parameter_string)
            if fuse_index is None:
                content, status = Endpoints.bad_request()
            else:
                content, status = Endpoints.fire(fuse_index)
        elif location == "/testloop":
            content, status = Endpoints.testloop()
        elif location == "/state":
            content, status = Endpoints.state()
        elif location == "update-device-ids":
            device_ids = self._extract_device_ids(parameter_string)
            if device_ids is None:
                content, status = Endpoints.bad_request()
            else:
                content, status = Endpoints.update_device_ids(device_ids)
        elif location == "shutdown":
            self._shutdown = True
            content, status = Endpoints.ok()
        else:
            content, status = Endpoints.not_found()

        print(f"{address} > {url} : {self.STATUS_STRING[status]}")

        self._current_connection.send(
            f"HTTP/1.0 {self.STATUS_STRING[status]}\r\n"
            + f"Content-type: {content_type}\r\n\r\n"
        )
        self._current_connection.send(content)
        self._current_connection.close()
