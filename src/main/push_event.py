from requests import Request
import json
from base64 import b64decode
from .logger import Logger
from config import config,Device

log = Logger(__name__)

class PushEvent():
    def __init__(self,request):
        self.request:Request = request
        self.event_type = None

    def parse(self):
        event_data = self.request.json
        log.info(f"data:{event_data}")
        data = event_data['message']['data']
        print(event_data['message']['publishTime'])
        json_data = json.loads(b64decode(data).decode('ascii'))
        log.info(f"json_data:{json_data}")

        event:dict = json_data['resourceUpdate']['events']
        event_id = list(event.values())[0]['eventId']
        event_type:str = list(event.keys())[0]


        url:str = json_data['resourceUpdate']['name']
        device_name = self.get_room(url)

        log.info(f'new event: {event_type}')

        self.event_type = event_type
        return url,event_id,device_name
    
    def skip_event(self):
        is_skipping = self.event_type != 'sdm.devices.events.CameraMotion.Motion' and self.event_type != 'sdm.devices.events.CameraPerson.Person'
        if is_skipping: log.info(f'skipping for event type: {self.event_type}')
        return is_skipping
    
    def get_room(self,device_code):
        for device in config.devices:
            if device.code in device_code:
                return device.name
        return Device.DEFAULT