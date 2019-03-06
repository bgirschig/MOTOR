# pylint: disable=E0611,E0401

""" utilities for saving/retrieving objects on gcs """

import os
from google.appengine.api import app_identity
import cloudstorage as gcs
import hashlib
from StringIO import StringIO
from common.utils import MIME2FORMAT
import time
from base64 import b64encode

bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
retry_params = gcs.RetryParams(backoff_factor=1.1)

def get_renders(request_id):
  folder_path = "/"+bucket_name+"/render_outputs/"+request_id+"/"
  return gcs.listbucket(folder_path, retry_params=retry_params)

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
  raise NotImplementedError("The upload_image function is deprecated, and no longer implemented")
  url = upload_file(file_handle, mime_type)
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

def get_signed_url(resource, delay=3600):
  """Return a signed URL for Google Cloud Storage access
  args:
      resource: ressource to get the url for
  kwargs:
      delay: time in seconds from now for which link is valid
  """
  method = "GET"
  content_md5 = ""
  content_type = ""
  expires = str(int(time.time()) + delay)

  blob = "\n".join([method, content_md5, content_type, expires, resource])
  _signing_key_name, signature = app_identity.sign_blob(blob)
  signature = b64encode(signature)
  signature = signature.replace(r"+", r"%2B").replace(r"/", r"%2F")
  
  url = "https://storage.googleapis.com{}?GoogleAccessId={}&Expires={}&Signature={}".format(
    resource,
    app_identity.get_service_account_name(),
    expires,
    signature
  )

  return url