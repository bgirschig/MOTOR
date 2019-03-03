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
from io import BytesIO
from google.appengine.api import images

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
  elif type(obj) == type(None):
    return obj
  else:
      raise Exception('unexpected value type: '+str(type(obj)))

def parseItem(field_name, fields, options):
  output = []
  values = fields.getall(field_name)
  for value in values:
    # files are uploaded and their urls are used in the request
    if file_utils.isFile(value):
      file_utils.checkFile_size(value.file, MAX_FILE_SIZE)
      # image converters
      if "convert_jpg" in options:
        value = convertFormFile(value, 'image/jpeg')
      elif "convert_png" in options:
        value = convertFormFile(value, 'image/png')
      output.append(upload_file(value.file, value.type))
   
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

"""
Converts the given File_field to another format.
Mime 'kinds' should match (image to image, text to text, etc...)
If the input already has the target mime type, the file object is returned.
"""
def convertFormFile(formValue, target_mime):
  output = File_field(formValue.file, formValue.type)

  # Mime types match. No need to convert
  if formValue.type == target_mime:
    return output
  
  data_kind, data_type = formValue.type.split("/")
  target_kind, target_type = target_mime.split("/")
  
  # convert images
  if data_kind == "image" and target_kind == "image":
    img = images.Image(formValue.file.getvalue())
    
    # App engine's image API requires at least one transform. This is a no-op
    # that gets around this limitation (we only need to convert the image
    # format)
    img.rotate(360)

    if target_type == "jpeg":
      output.file = BytesIO(img.execute_transforms(output_encoding=images.JPEG))
      output.type = 'image/jpg'
    elif target_type == "png":
      output.file = BytesIO(img.execute_transforms(output_encoding=images.PNG))
      output.type = 'image/png'
    elif target_type == "webp":
      output.file = BytesIO(img.execute_transforms(output_encoding=images.WEBP))
      output.type = 'image/webp'
    else:
      raise ValueError("No converter defined to {} image".format(target_type))

  else:
    raise TypeError("No converter defined from types {} to {}".format(
      formValue.type,
      target_mime,
    ))
  return output

class File_field():
  def __init__(self, file_, mime_type):
    self.file = file_
    self.type = mime_type