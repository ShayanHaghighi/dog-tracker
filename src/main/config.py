import os
from dotenv import load_dotenv
from .logger import Logger
from .constants import CFG_PATH
import json

logger = Logger(__name__)

class Device():
    DEFAULT='tbd'
    
    def __init__(self, name, code):
        self.name = name
        self.code = code

class Config():
    
    ENV_PATH = f'{CFG_PATH}/.env'
    DEVICES_PATH = f'{CFG_PATH}/devices.json'
    
    def __init__(self):
        logger.debug('loading env variables')
        load_dotenv(dotenv_path=self.ENV_PATH)
        self.project_id = self.get_env('PROJECT_ID')
        self.access_token = self.get_env('ACCESS_TOKEN')
        self.client_id = self.get_env('CLIENT_ID')
        self.client_secret = self.get_env('CLIENT_SECRET')
        self.refresh_token = self.get_env('REFRESH_TOKEN')
        self.devices: list[Device] = []
        with open(self.DEVICES_PATH) as json_file:
            deviceList = json.load(json_file)
            for device in deviceList:
                self.devices.append(Device(device['room_name'],device['device_id']))
        
        # self.devices = []
        
        # with open(self.DEVICES_PATH, 'r') as devices_json:
 
        #     devices_json = json.load(devices_json)
        #     for device in devices_json:
        #         self.devices.append(Device(json=device))
            
        logger.debug('env variables loaded')


        
    def get_env(self,var_name:str):
        env = os.getenv(var_name)
        if not env:
            logger.warning(f'env var: {var_name} is not set')
        return env or ''

    def update_access_token(self,access_token:str) -> None:
        self.access_token = access_token

        with open(self.ENV_PATH, 'r') as file:
            lines = file.readlines()

        with open(self.ENV_PATH+'_new', 'w+') as file:
            for line in lines:
                if line.startswith(f'{'ACCESS_TOKEN'}='):
                    file.write(f'{'ACCESS_TOKEN'}={access_token}\n')
                else:
                    file.write(line)
        os.remove(self.ENV_PATH)
        os.rename(self.ENV_PATH+'_new',self.ENV_PATH)
        
                    
config = Config()
