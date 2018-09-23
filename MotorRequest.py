import json
from time import time
import hashlib
from random import randrange
import logging


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
        raise NotImplementedError()