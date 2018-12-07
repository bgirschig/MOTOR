# pylint: disable=E0611,E0401

""" utilities for saving/retrieving objects on gcs """

import os
from google.appengine.api import app_identity
import cloudstorage as gcs
import hashlib
from PIL import Image
from StringIO import StringIO
from common.utils import MIME2FORMAT

bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
retry_params = gcs.RetryParams(backoff_factor=1.1)

def upload_file(file, file_type="application/octet-stream"):
  """ Upload a file to gcloud storage. The file is saved to a location
  determined by its hash, so that we only upload the same file once.
  
  Arguments:
    file {file} -- A file-like object, to upload
  
  Returns:
    string -- the cloud storage path to the uploaded file
  """

  content = file.read()
  file_hash = hashlib.sha512()
  file_hash.update(content)
  file_path = "/" + bucket_name + "/uploads/" + file_hash.hexdigest()

  if not cloud_file_exists(file_path):
    with gcs.open(file_path, "w", content_type=file_type, retry_params=retry_params) as f:
      f.write(content)

  return "gs:/"+file_path

def upload_image(file_handle, mime_type):
  """ Uploads the given image to cloud storage. Converts it if the mime type is
  different form the image type
  
  Arguments:
    file_handle {file} -- the file-like object containing the image
    mime_type {string} -- mime type of the saved image. if the type is
    different, the image gets converted
  
  Raises:
    TypeError -- if the given mime type is not known/not an image
  
  Returns:
    string -- url to the uploaded image on cloud storage
  """
  
  is_image = mime_type.split('/')[0] == "image"
  if mime_type not in MIME2FORMAT or not is_image:
    raise TypeError("unexpected mime type:", mime_type)

  img = Image.open(StringIO(file_handle.read()))
  img = img.convert("RGB")
  
  new_img = StringIO()
  img.save(new_img, MIME2FORMAT[mime_type])
  new_img.seek(0)
  url = upload_file(new_img, mime_type)
  return url

def cloud_file_exists(filepath):
  """Checks wether a file exists on gcs
  
  Arguments:
    filepath {string}
  
  Returns:
    bool
  """
  try:
    return gcs.stat(filepath)
  except gcs.errors.NotFoundError as e:
    return False