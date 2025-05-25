from cv2 import VideoCapture,rectangle
import cv2
from ultralytics import YOLO
import numpy as np
from datetime import datetime

from ..logger import Logger
from ..constants import RESOURCES_PATH

logger = Logger(__name__)
model = YOLO(f'C:/Users/shaya/Coding-Projects(NEW)/dog-tracker/runs/detect/train3/weights/best.pt')
# # 4,2,3
# def scan_videocap(cap:VideoCapture):
#     if not cap.isOpened():
#         logger.info("Error: Couldn't open stream.")
#         pass
#     else:
#         # while True:
#             # logger.info("Stream %s successfully opened",device.room_name)

#             ret, frame = cap.read()
#             if not ret:
#                 logger.info("Failed to retrieve frame.")
#                 return
#             smaller_frame = cv2.resize(frame, (0,0),fx=0.5,fy=0.5)
#             find_dog(smaller_frame)
#             cv2.imshow('RTSPS Stream', smaller_frame)

#             while True:
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     cap.release()
#                     cv2.destroyAllWindows()
#                     break

def scan_image(content:bytes,device_name,scale=0.5):
    image_np = np.frombuffer(content, np.uint8)
    frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)  
    file_name = str(datetime.now().strftime('%Y%m%d-%H%M%S'))
    
    smaller_frame = cv2.resize(frame, (0,0),fx=scale,fy=scale)
    if find_dog(smaller_frame):
        logger.info('dog found')

        file_path = f"{RESOURCES_PATH}/images/dogFound/{file_name}.jpg"
        with open(file_path, "wb") as file:
            file.write(content)
            logger.info(f'saved image to {file_path}')

        # cv2.imshow('Image', smaller_frame)

        # while True:
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         cv2.destroyAllWindows()
        #         break
        return True
    else:
        logger.info('dog not found')
        file_path = f"{RESOURCES_PATH}/{device_name}/{file_name}.jpg"
        with open(file_path, "wb") as file:
            file.write(content)
            logger.info(f'saved image to {file_path}')
        return False


def find_dog(frame):
    results = model(frame)
    result = results[0]

 

    # result.show()
    # return
    boxes = result.boxes.xyxy  
    class_ids = result.boxes.cls 
    scores = result.boxes.conf 

    # print(class_ids)
    
    DOG_ID = 16.

    mask = (class_ids == DOG_ID)

    filtered_class_ids = class_ids[mask]
    filtered_boxes = boxes[mask]
    filtered_scores = scores[mask]

    
    for box in filtered_boxes:
        x1, y1, x2, y2 = map(int, box)
        rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return len(filtered_boxes)>0

# path2 = f'{RESOURCES_PATH}/images/dogFound'
# # path1 = f'{RESOURCES_PATH}/images/dogShouldBeFound'

# def files_in(path):
#     return [os.path.join(path,file_name) for file_name in os.listdir(path)]
# hits = {}
# import os
# for file_name in files_in(path2):
#     for i in range (5,6):
#         i=i/10
#         hits[i] = 0
#         with open(file_name, "rb") as file:
#             if scan_image(file.read(),scale=i):
#                 hits[i] += 1

# print(hits)