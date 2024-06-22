import cv2
from PIL import Image
from ultralytics import YOLO


model = YOLO('yolov8n.pt')


def find_dog(frame):
    results = model(frame)
    result = results[0]

    # print(result.boxes)
    # im_bgr = result.plot()
    # im_rbg = Image.fromarray(im_bgr[::-1])
    # result.show()
    # return
    boxes = result.boxes.xyxy  
    class_ids = result.boxes.cls 
    scores = result.boxes.conf 

    print(class_ids)
    
    DOG_ID = 16.

    mask = (class_ids == DOG_ID)

    filtered_class_ids = class_ids[mask]
    filtered_boxes = boxes[mask]
    filtered_scores = scores[mask]

    
    for box in filtered_boxes:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    