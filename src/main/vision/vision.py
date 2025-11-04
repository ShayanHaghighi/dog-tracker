import typing
from cv2 import rectangle
import cv2
from ultralytics import YOLO  # type: ignore
import numpy as np
from datetime import datetime
from cv2.typing import MatLike
from ..utils.logger import Logger
from ..utils.constants import RESOURCES_PATH
from ..utils.config import config

logger = Logger(__name__)
# model = YOLO(
#     "C:/Users/shaya/Coding-Projects(NEW)/DogTrackerProject/dog-tracker/src/resources/model/best.pt"
# )
MODEL_DIR = "C:/Users/shaya/Coding-Projects-NEW/DogTrackerProject/dog-tracker/src/resources/model/"
CONFIDENCE_THRESHOLD = 0.3


class VisionClient:
    def __init__(self) -> None:
        self.models = {}
        self.load_models()

    def load_models(self):
        self.models = {
            room: YOLO(f"{MODEL_DIR}/{room}.pt", task="detect")
            for room in config.devices.values()
        }

    def scan_image(self, content: bytes, device_name: str, scale: float = 0.5):
        image_np = np.frombuffer(content, np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        file_name = str(datetime.now().strftime("%Y%m%d-%H%M%S"))

        smaller_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        file_path = f"{RESOURCES_PATH}/{device_name}/{file_name}.jpg"
        self.save_image(content, file_path)

        dog_is_found: bool = self.find_dog(smaller_frame, device_name)
        logger.info("dog found" if dog_is_found else "dog not found")

        return dog_is_found

    def save_image(self, content: bytes, file_path: str):
        with open(file_path, "wb") as file:
            file.write(content)
            logger.info(f"saved image to {file_path}")

    def find_dog(self, frame: MatLike, room_name: str):
        results: list[typing.Any] = self.models[room_name](frame)  # type: ignore
        result = results[0]

        boxes = result.boxes.xyxy
        class_ids = result.boxes.cls
        scores = result.boxes.conf
        # TODO: store high confidence value

        DOG_ID = 16.0

        mask = class_ids == DOG_ID

        # filtered_class_ids = class_ids[mask]
        filtered_boxes = boxes[mask]
        filtered_scores = scores[mask]
        # if filtered_scores:
        #     logger.info(f"filtered scored: {filtered_scores}")

        logger.info(f"filtered scored: {filtered_scores}")
        # TODO: is this needed?
        for box in filtered_boxes:
            x1, y1, x2, y2 = map(int, box)
            rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return len(filtered_boxes) > 0


visionClient = VisionClient()
