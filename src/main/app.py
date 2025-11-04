from flask import Flask, request
from .utils.logger import Logger
from .api.imageURLClient import ImageUrlClient
from .api.push_event import PushEvent
from .api.imageProcessClient import process_image
from .vision.vision import visionClient

logger = Logger("app")

app = Flask(__name__)

# https://cool-naturally-hagfish.ngrok-free.app/nest-webhook


@app.route("/nest-webhook", methods=["POST"])
def handle_event():
    try:
        event = PushEvent(request)
        url, event_id, device_name = event.parse()

        if event.skip_event():
            return "", 204

        urlClient = ImageUrlClient(url, event_id)
        url, token, error_msg = urlClient.get_response()

        if error_msg:
            logger.error(error_msg)
            return "", 204

        process_image(url, token, device_name)
    except KeyError as e:
        logger.error(e)

    return "", 204  # Acknowledge the message


@app.route("/reload", methods=["POST"])
def reload_models():
    visionClient.load_models()
    return "", 204


if __name__ == "__main__":
    logger.info("Server Starting...")
    app.run(port=8081)
