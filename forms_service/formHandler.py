# pylint: disable=E0611,E0401

import webapp2
import json
import cloudstorage as gcs
from google.appengine.api import app_identity
import os
from os import path
import uuid
import math

MAX_FILE_SIZE = 1 * 10**6
bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

class FormHandler(webapp2.RequestHandler):
  def post(self):
    fields = dict(self.request.POST)
    for key in fields.keys():
      field = fields[key]
      if isFile(field):
        # Upload file to gcs, and replace the file object in the data by the url
        # to that file in gcs
        file_size = get_file_size(field) 
        if file_size > MAX_FILE_SIZE:
          human_max_size = str(math.floor(MAX_FILE_SIZE/1000))+"KB"
          human_size = str(math.floor(file_size/1000))+"KB"
          raise FileSizeExceeded("Uploaded files must be {} or lower. the file in field [{}] is {}".format(human_max_size, key, human_size))
        fields[key] = upload_file(field)
      
      parts = key.split("_")      
      # handle the 'other' fields from select and radio types
      if len(parts) == 2 and parts[0] in fields and parts[1] == "other":
        if fields[parts[0]] == "other":
          fields[parts[0]] = field
        del fields[key]

    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(json.dumps(fields, indent=2))

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