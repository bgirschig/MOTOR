import uuid
import os
from google.appengine.api import app_identity
import cloudstorage as gcs
import hashlib
from google.appengine.api import images
from google.appengine.ext import blobstore
from PIL import Image
from StringIO import StringIO

bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
retry_params = gcs.RetryParams(backoff_factor=1.1)

MIME2FORMAT = {
  "image/jpeg": "JPEG",
  "image/jpg": "JPEG",
  "image/png": "PNG",
  "image/bmp": "BMP",
  "image/gif": "GIF",
  "image/tiff": "TIFF",
  "image/webp": 'WebP'
}

def upload_file(file, file_type="application/octet-stream"):
  """Upload a file to gcloud storage (destination is determined automatically)
  
  Arguments:
    file {file} -- A file-like object, to upload
  
  Returns:
    string -- the cloud storage path to the uploaded file
  """

  content = file.read()
  file_hash = hashlib.sha512()
  file_hash.update(content)
  file_path = "/" + bucket_name + "/uploads/" + file_hash.hexdigest()

  if not file_exists(file_path):
    with gcs.open(file_path, "w", content_type=file_type, retry_params=retry_params) as f:
      f.write(content)

  return "gs:/"+file_path

def upload_image(file_handle, mime_type):
  if mime_type not in MIME2FORMAT:
    raise TypeError("unexpected mime type:", mime_type)

  img = Image.open(StringIO(file_handle.read()))
  img = img.convert("RGB")
  
  new_img = StringIO()
  img.save(new_img, MIME2FORMAT[mime_type])
  new_img.seek(0)
  url = upload_file(new_img, mime_type)
  return url

def file_exists(filepath):
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