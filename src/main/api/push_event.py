import typing

# from requests import Request
from flask.wrappers import Request
import json
from base64 import b64decode
from ..utils.logger import Logger
from ..utils.config import config, Device

log = Logger(__name__)


class PushEvent:
    def __init__(self, request: Request):
        self.request: Request = request
        self.event_type: str = ""

    def parse(self) -> tuple[str, str, str]:
        event_data = self.request.json
        if event_data:
            json_data = json.loads(
                b64decode(event_data["message"]["data"]).decode("ascii")
            )
            log.info(f"json_data:{json_data}")

            event: dict[str, typing.Any] = json_data["resourceUpdate"]["events"]
            event_id: str = list(event.values())[0]["eventId"]
            self.event_type: str = list(event.keys())[0]
            log.info(f"new event: {self.event_type}")

            url: str = json_data["resourceUpdate"]["name"]
            device_name = self.get_room(url)
            log.info(f"request is for room: {device_name}")

            return url, event_id, device_name
        raise Exception(f"found no eventdata: {self.request.json}")

    def skip_event(self):
        is_skipping = (
            self.event_type != "sdm.devices.events.CameraMotion.Motion"
            and self.event_type != "sdm.devices.events.CameraPerson.Person"
        )
        if is_skipping:
            log.info(f"skipping for event type: {self.event_type}")
        return is_skipping

    def get_room(self, url: str) -> str:
        for device_id, room_name in config.devices.items():
            if device_id in url:
                return room_name
        return Device.DEFAULT
