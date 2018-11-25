# pylint: disable=E0611,E0401

import webapp2
import json
import cloudstorage as gcs
from google.appengine.api import app_identity
import os
from os import path
import uuid
import math
import yaml

MAX_FILE_SIZE = 1 * 10**6
bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

other_suffix = "_other"
other_suffix_length = len(other_suffix)

class FormHandler(webapp2.RequestHandler):
  def post(self):
    fields = dict(self.request.POST)
    
    definition_path = fields["form_definition"]
    with open(definition_path, 'r') as f:
      form_definition = yaml.load(f)
    
    print form_definition
    output = form_definition["output"]
    output = extractData(output, self.request.POST, form_definition)

    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(output, indent=2))

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
    if isFile(value):
      checkFile_size(value)
      output.append(upload_file(value))
    elif(value == "other" and field_name+other_suffix in fields):
      output.append(fields[field_name+other_suffix])
    else:
      output.append(fields[field_name])
  
  if("multi" not in options):
    output = output[0]
  return output

def isFile(item):
  try:
    return bool(item.file)
  except AttributeError:
    return False

def get_file_size(file):
  file.file.seek(0, 2)
  size = file.file.tell()
  file.file.seek(0)
  return size

def checkFile_size(file):
  file_size = get_file_size(file) 
  if file_size > MAX_FILE_SIZE:
    human_max_size = str(math.floor(MAX_FILE_SIZE/1000))+"KB"
    human_size = str(math.floor(file_size/1000))+"KB"
    raise FileSizeExceeded("Uploaded files must be {} or lower. the given file is {}".format(human_max_size, human_size))

def upload_file(file):
  content = file.file.read()
  file_name = str(uuid.uuid4())
  file_type = file.type        
  file_path = "/" + bucket_name + "/uploads/" + file_name

  # TODO: Use file hash as name, and check if it already exists before uploading

  write_retry_params = gcs.RetryParams(backoff_factor=1.1)
  with gcs.open(
      file_path, "w", content_type=file_type,
      retry_params=write_retry_params) as f:
    f.write(content)

  return "gs:/"+file_path

class FileSizeExceeded(Exception):
    pass