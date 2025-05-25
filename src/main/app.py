from flask import Flask, request
from .logger import Logger
from .clients.imageURLClient import ImageUrlClient
from .push_event import PushEvent
from .clients.imageProcessClient import process_image

logger = Logger('app')

app = Flask(__name__)

# https://cool-naturally-hagfish.ngrok-free.app/nest-webhook


@app.route('/nest-webhook', methods=['POST'])
def handle_event():

    event = PushEvent(request)
    url,event_id,device_name = event.parse()
    
    if event.skip_event():
        return '',204
    
    urlClient = ImageUrlClient(url,event_id)
    url,token,error_msg = urlClient.get_response()

    if error_msg:
        logger.error(error_msg)
        return '',204
    

    process_image(url,token,device_name)

    
    return '', 204  # Acknowledge the message

if __name__ == "__main__":
    logger.info('Server Starting...')
    app.run(port=8080)
