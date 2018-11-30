# pylint: disable=E0611,E0401

import webapp2
import json
import os
from os import path
import math
import yaml
from utils import upload_file

MAX_FILE_SIZE = 1 * 10**6

other_suffix = "_other"
other_suffix_length = len(other_suffix)

class FormHandler(webapp2.RequestHandler):
  def post(self):
    fields = dict(self.request.POST)
    
    definition_path = fields["form_definition"]
    with open(definition_path, 'r') as f:
      form_definition = yaml.load(f)
    
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
      checkFile_size(value.file)
      output.append(upload_file(value.file, value.type))
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
  file.seek(0, 2)
  size = file.tell()
  file.seek(0)
  return size

def checkFile_size(file):
  file_size = get_file_size(file) 
  if file_size > MAX_FILE_SIZE:
    human_max_size = str(math.floor(MAX_FILE_SIZE/1000))+"KB"
    human_size = str(math.floor(file_size/1000))+"KB"
    raise FileSizeExceeded("Uploaded files must be {} or lower. the given file is {}".format(human_max_size, human_size))

class FileSizeExceeded(Exception):
    pass