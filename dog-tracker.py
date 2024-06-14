import cv2
import requests
import os
import logging
from dotenv import load_dotenv, find_dotenv
from PIL import Image
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

open('rtsp.log', 'w').close()
logger = logging.getLogger(__name__)
logging.basicConfig(filename='rtsp.log',level=logging.INFO)
load_dotenv()
logger.info("Started")
project_id = os.getenv('PROJECT_ID')
device_ids = os.getenv('DEVICE_IDS').split(',')
access_token = os.getenv('ACCESS_TOKEN')
refresh_token = os.getenv('REFRESH_TOKEN')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
old_rtsp_urls = os.getenv('OLD_RTSP_URLS').split(',')
logger.info("Loaded env variables")



def set_env_var(key:str, value:str) -> None:
    dotenv_path = find_dotenv()
    if dotenv_path == "":
        with open('.env', 'w') as f:
            f.write(f'{key}={value}\n')
    else:
        load_dotenv(dotenv_path)

        with open(dotenv_path, 'r') as file:
            lines = file.readlines()

        variable_exists = False
        with open(dotenv_path, 'w') as file:
            for line in lines:
                if line.startswith(f'{key}='):
                    file.write(f'{key}={value}\n')
                    variable_exists = True
                else:
                    file.write(line)

            if not variable_exists:
                file.write(f'{key}={value}\n')

def refresh_access_token():
    url = 'https://www.googleapis.com/oauth2/v4/token'
    params = {
        'client_id' : client_id,
        'client_secret' : client_secret,
        'refresh_token' : refresh_token,
        'grant_type' : 'refresh_token'
    }
    r = requests.post(url,params=params)

    if r.status_code == requests.codes.ok:
            logger.info("access token successfully refreshed")

    response_dict = r.json()
    new_token = response_dict['access_token']
    set_env_var('ACCESS_TOKEN',new_token)
    return new_token


def send_RTSP_request(access_token:str,device_id:str):
    url = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + project_id + '/devices/' + device_id + ':executeCommand'
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : 'Bearer ' + access_token
    }
    payload = {
        "command" : "sdm.devices.commands.CameraLiveStream.GenerateRtspStream",
        "params" : {}
    }
    r = requests.post(url,headers=headers,json=payload)
    if r.status_code == requests.codes.ok:
        logger.info("rtsp url successfully retrieved")
    return r


def get_RTSP_url(device_id:str):
    global access_token
    r = send_RTSP_request(access_token,device_id)
    if r.reason == "Unauthorized":
        logger.info("access token expired - refreshing token")

        access_token = refresh_access_token()
        r = send_RTSP_request(access_token,device_id)

    r.raise_for_status()
    # print(access_token)
    response_dict = r.json()

    # print("rtsp url: " + response_dict['results']['streamUrls']['rtspUrl'])

    return response_dict['results']['streamUrls']['rtspUrl']

def show_livestream(device_id:str,idx:int):

    logger.info("Capturing Stream %d",idx)
    cap = cv2.VideoCapture(old_rtsp_urls[idx])
    if not cap.isOpened():
        logger.info("RTSPS URL expired - retrieving new url")
        rtsps_url = get_RTSP_url(device_id)
        old_rtsp_urls[idx] = rtsps_url
        cap = cv2.VideoCapture(rtsps_url)

    if not cap.isOpened():
        logger.info("Error: Couldn't open stream.")
    else:
        # while True:
            logger.info("Stream %d successfully opened",idx)

            ret, frame = cap.read()
            if not ret:
                logger.info("Failed to retrieve frame.")
                return
            smaller_frame = cv2.resize(frame, (0,0),fx=0.5,fy=0.5)
            results = model(smaller_frame)
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
                cv2.rectangle(smaller_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            cv2.imshow('RTSPS Stream', smaller_frame)

            while True:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    # break

                    cap.release()
                    cv2.destroyAllWindows()
                    break

def show_all_streams():
    # show_livestream(device_id=device_ids[3],idx=3)
    # return

    for idx,device_id in enumerate(device_ids):
        show_livestream(device_id,idx)

    url_string = ""

    for url in old_rtsp_urls:
        url_string += url + ','

    url_string = url_string[:-1]

    set_env_var('OLD_RTSP_URLS',url_string)

    

# show_livestream()
show_all_streams()