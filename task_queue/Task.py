from google.appengine.ext import ndb
from protorpc import messages
from google.appengine.ext.ndb import msgprop
import time
import datetime
class Status(messages.Enum):
  PENDING = 0
  RUNNING = 1
  DONE = 2
  FAILED = 3

class Task(ndb.Model):
  status = msgprop.EnumProperty(Status, default=Status.PENDING)
  create_time = ndb.DateTimeProperty(auto_now_add=True)
  payload = ndb.JsonProperty(default={'info': 'empty payload'})
  response = ndb.JsonProperty(default={'info': 'empty reponse'})
  tags = ndb.StringProperty(repeated=True)
  api_version = ndb.StringProperty(default="0.0.1")
  attempt_count = ndb.IntegerProperty(default=0)
  max_attempts = ndb.IntegerProperty(default=5)
  lease_timeout = ndb.DateTimeProperty()

  def toDict(self):
    return {
      'status': self.status.name,
      'create_time': time.mktime(self.create_time.timetuple()),
      'payload': self.payload,
      'tags': self.tags,
      'api_version': self.api_version,
      'key': self.key.urlsafe(),
      'attempt_count': self.attempt_count,
      'max_attempts': self.max_attempts,
      'lease_timeout': time.mktime(self.lease_timeout.timetuple()) if self.lease_timeout else None,
      'lease_timeout_str': str(self.lease_timeout),
      'now': str(datetime.datetime.now()),
    }