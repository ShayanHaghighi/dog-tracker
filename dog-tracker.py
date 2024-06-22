import cv2
import requests
import os
import logging
from dotenv import load_dotenv, find_dotenv
from vision import find_dog
from interactiveCLUI import select_option


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

def load_env():
    pass

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

def refresh_access_token() -> None:
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


def send_RTSP_request(access_token:str,device_id:str) -> str:
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


def get_RTSP_url(device_id:str) -> None:
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

# gets the stream for a particular device
def getStream(device_id:str, idx:int):
    cap = cv2.VideoCapture(old_rtsp_urls[idx])
    if not cap.isOpened():
        logger.info("RTSPS URL expired - retrieving new url")
        rtsps_url = get_RTSP_url(device_id)
        old_rtsp_urls[idx] = rtsps_url
        cap = cv2.VideoCapture(rtsps_url)
    
    return cap

# searches for a dog in the livestream for a particular device
def search_stream(device_id:str, idx:int) -> None:

    logger.info("Capturing Stream %d",idx)
    
    cap = getStream(device_id,idx)

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
            find_dog(smaller_frame)
            cv2.imshow('RTSPS Stream', smaller_frame)

            while True:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    break

# updates the values in .env file
def update_rtsp_env() -> None:
    url_string = ""
    for url in old_rtsp_urls:
        url_string += url + ','
    set_env_var('OLD_RTSP_URLS',url_string[:-1])

def search_all_streams() -> None:

    for idx,device_id in enumerate(device_ids):
        search_stream(device_id,idx)

    update_rtsp_env()

    
if __name__=='__main__':
    answer,_ = select_option("which device do you want to access?",["All","One specific one"])
    if answer == "All":
        search_all_streams()
    else:
        answer,idx = select_option("which room do you want to access?",["1","2","3","4","5",])
        search_stream(device_id=device_ids[idx],idx=idx)