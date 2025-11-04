from requests import Response,codes
from .sdmClient import SdmClient
from ..utils.logger import Logger

logger = Logger(__name__)

class ImageUrlClient(SdmClient):
    
    def __init__(self,url:str,event_id:str):
        super().__init__()
        self.url:str = url
        self.event_id:str = event_id
    

    def get_response(self):
        response:Response = self.make_request(
            endpoint=f'{self.url}:executeCommand',
            payload={"command" : "sdm.devices.commands.CameraEventImage.GenerateImage",
                    "params" : { "eventId" : f"{self.event_id}"}
                    }
        )

        logger.debug(response.text)

        json_response = response.json()

        if response.status_code != codes.ok:
            error_msg = f'error {response.status_code} - {json_response['error']['message']}'
            return '','',error_msg
        
        logger.info('received GenerateImage url')
            
        url = json_response['results']['url']
        token = json_response['results']['token']

        return url,token,None
