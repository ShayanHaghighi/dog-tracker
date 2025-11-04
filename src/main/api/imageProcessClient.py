from requests import get
from ..vision.vision import visionClient
from ..utils.logger import Logger

logger = Logger(__name__)


def process_image(image_url: str, token: str, device_name: str) -> None:
    response = get(
        image_url + "?width=1080", headers={"Authorization": f"Basic {token}"}
    )

    if response.status_code == 200:
        logger.info("scanning image")
        visionClient.scan_image(response.content, device_name)

    else:
        print(f"Failed to fetch image: {response.status_code} - {response.text}")
        raise Exception()
