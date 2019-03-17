from google.appengine.ext import ndb
from protorpc import messages
from google.appengine.ext.ndb import msgprop
import time
import datetime
import json

class Form(ndb.Model):
  name = ndb.TextProperty(required=True, indexed=True)
  content = ndb.TextProperty(default="# empty form", indexed=False)
  create_time = ndb.DateTimeProperty(auto_now_add=True)
  update_time = ndb.DateTimeProperty(auto_now=True)

  def toDict(self):
    return {
      'name': self.name,
      'content': self.content,
      'create_time': time.mktime(self.create_time.timetuple()),
      'update_time': time.mktime(self.update_time.timetuple()),
    }
  
  def serialize(self):
    return json.dumps(self.toDict())