from requests import get
from .vision import scan_image
from ..logger import Logger

logger = Logger(__name__)

def process_image(image_url,token,device_name):
    response = get(image_url+'?width=1080', headers={'Authorization':f"Basic {token}"})
    
    if response.status_code == 200:
        logger.info('scanning image')
        scan_image(response.content,device_name)

    else:
        print(f"Failed to fetch image: {response.status_code} - {response.text}")
        raise Exception()


