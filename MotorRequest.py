import json
from time import time
import hashlib
from random import randrange
import logging
from google.appengine.api import urlfetch

ACCEPT_STATUS_CODES = [200, 201, 202]
RENDERER_API_URL = 'http://40.89.131.172:8081/render'

class MotorRequest:
    """Generic request to the Motor service"""

    def __init__(self, clientID, requesterID, data):
        self.clientID = clientID
        self.requesterID = requesterID
        self.data = data
        self.timestamp = time()

        # Default random id. This serves 2 purposes:
        #   - Allow calling the toString function, in the hashing function below
        #   - Reduce collision risks: the exact same request parameters should
        #   not give the same request id
        # TODO: Actually check for collisions in the database ?
        self.id = randrange(0, 100000000000000)
        # Get a string representation of this request, to create the hash / id
        string_self = self.toString()
        # replace id with new value
        self.id = hashlib.md5(string_self).hexdigest()
    
    def toString(self):
        """
        Returns:
            string -- the serialized request
        """

        obj = {
            'clientID': self.clientID,
            'requesterID': self.requesterID,
            'data': self.data,
            'timestamp': self.timestamp,
            'id': self.id,
        }
        
        return json.dumps(obj)

    def send(self):
        request_data = {
            "template": "chanel_test",
            "compName": "main",
            "id": self.id,
            "resources": [
                {"target": "main_image.jpg", "source": self.data['images'][0]},
                {"target": "data.json", 'data': self.data},
            ],
            "encoders": [
                {"presetName": "smol_vid", "filename": "video_a"},
            ]
        }

        try:
            headers = {'Content-Type': 'application/json'}
            result = urlfetch.fetch(
                url=RENDERER_API_URL,
                method=urlfetch.POST,
                payload=json.dumps(request_data),
                headers=headers
            )
            logging.info({
                'tag': 'render-request',
                'message': 'successfully placed request',
                'request_data': request_data,
            })
            if result.status_code not in ACCEPT_STATUS_CODES:
                raise Exception('failed request: [{}] {}'.format(
                    result.status_code, result.content))
        except Exception as err:
            logging.error({
                'tag': 'render-request',
                'type': type(err).__name__,
                'message': err.message,
                'request_data': request_data,
            })
