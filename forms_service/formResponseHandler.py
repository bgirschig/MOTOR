# pylint: disable=E0611,E0401

""" Handles the response to a MOTOR form: parses its data according to the form
definition and returns a formatted dictionnary.
"""

import webapp2
import json
import yaml
from common import storage_utils
from common import file_utils
from common import utils
from common.task_queue_client import Queue
from google.appengine.api import users
from io import BytesIO
from google.appengine.api import images
from jinja_config import jinja

# config
MAX_FILE_SIZE = 8 * utils.MB
other_suffix = "_other"

# misc
queue = Queue()
other_suffix_length = len(other_suffix)

class FormResponseHandler(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if not user: raise Exception("user should be logged in")

    fields = dict(self.request.POST)
    definition_path = fields["form_definition"]
    with open(definition_path, 'r') as f:
      form_definition = yaml.load(f)

    if "task" in form_definition:
      payload = form_definition["task"]["payload"]
      payload = extractData(payload, self.request.POST, form_definition)
      payload["clientID"] = user.email()

      tags = form_definition["task"].get("tags", [])
      tags.append('forms-service')

      max_attempts = form_definition["task"].get("max_attempts", None)

      task = queue.appendTask(payload, tags, max_attempts)
      url = queue.get_task_url(task["task_key"])

      response = jinja.get_template('response.html').render({
        "task_url": url,
        "task_key": task["task_key"],
        "message": form_definition["formSuccessMessage"],
        "is_admin": users.is_current_user_admin()
      })
      self.response.write(response)
    else:
      raise NotImplementedError("Custom form handling is not implemented yet (only task-based)")

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
  elif type(obj) == type(None):
    return obj
  else:
      raise Exception('unexpected value type: '+str(type(obj)))

def parseItem(field_name, fields, options):
  output = []
  values = fields.getall(field_name)
  for value in values:
    # Files are uploaded and their urls are used in the request
    if file_utils.isFile(value):
      # Ensure the file is not too big
      file_utils.checkFile_size(value.file, MAX_FILE_SIZE, value.filename)
      # image converters
      src_file = value.file.getvalue()
      if "convert_jpg" in options:
        converted, mime = storage_utils.convert(src_file, value.type, 'image/jpeg')
        value = File_field(converted, mime)
      elif "convert_png" in options:
        converted, mime = storage_utils.convert(src_file, value.type, 'image/png')
        value = File_field(converted, mime)
      else:
        pass

      # files are uploaded and we store their url in the form response
      output.append(storage_utils.upload_file(value.file, value.type))
   
    # If there is an "_other" option in a choices list, the form renderer adds
    # an input field to specify what that "other" is, with the name:
    # <field_name><other_suffix>, eg. 'language_other'
    elif(value == "other" and field_name+other_suffix in fields):
      output.append(fields[field_name+other_suffix])
    
    # for 'normal' fields, simply add them to the output
    else:
      output.append(fields[field_name])
  
  if("multi" not in options):
    output = output[0] if len(output)>0 else None
  return output

class File_field():
  def __init__(self, file_, mime_type):
    self.file = file_
    self.type = mime_type