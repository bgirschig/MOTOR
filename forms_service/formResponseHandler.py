# pylint: disable=E0611,E0401

""" Handles the response to a MOTOR form: parses its data according to the form
definition and returns a formatted dictionnary.
"""

import webapp2
import json
import yaml
from common.storage_utils import upload_file
from common import file_utils
from common import utils
from common.task_queue_client import Queue
from google.appengine.api import users

# config
MAX_FILE_SIZE = 1 * utils.MB
other_suffix = "_other"

# misc
queue = Queue()
other_suffix_length = len(other_suffix)

class FormResponseHandler(webapp2.RequestHandler):
  def post(self):
    fields = dict(self.request.POST)
    
    definition_path = fields["form_definition"]
    with open(definition_path, 'r') as f:
      form_definition = yaml.load(f)
    
    payload = form_definition["output"]
    payload = extractData(payload, self.request.POST, form_definition)

    user = users.get_current_user()
    if not user:
      raise Exception("user should be logged in")
    payload["clientID"] = user.email()

    task = queue.appendTask(payload, ["render", "form"])

    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(task, indent=2))

def extractData(obj, fields, form_definition):
  if type(obj) == str or type(obj) == unicode:
    return obj
  elif type(obj) == list:
    return [extractData(item, fields, form_definition) for item in obj]
  elif type(obj) == dict:
    for key in obj:
      if key.startswith("field_"):
        new_key = key.replace("field_", "")
        try:
          field_name, options = obj[key].split("/") 
          options=options.split(',')
        except ValueError:
          field_name = obj[key]
          options = {}
        obj[new_key] = parseItem(field_name, fields, options)
        del obj[key]
      else:
        obj[key] = extractData(obj[key], fields, form_definition)
    return obj
  else:
      raise Exception('unexpected value type: '+type())

def parseItem(field_name, fields, options):
  output = []
  values = fields.getall(field_name)
  for value in values:
    if file_utils.isFile(value):
      file_utils.checkFile_size(value.file, MAX_FILE_SIZE)
      output.append(upload_file(value.file, value.type))
    elif(value == "other" and field_name+other_suffix in fields):
      output.append(fields[field_name+other_suffix])
    else:
      output.append(fields[field_name])
  
  if("multi" not in options):
    output = output[0]
  return output
