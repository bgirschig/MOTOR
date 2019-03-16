""" various utilities, too small to justify their own module """

from google.appengine.api import images

MIME2FORMAT = {
  "image/jpeg": images.JPEG,
  "image/jpg": images.JPEG,
  "image/png": images.PNG,
  "image/bmp": images.BMP,
  "image/gif": images.GIF,
  "image/tiff": images.TIFF,
  "image/webp": images.WEBP
}
FORMAT2MIME = {MIME2FORMAT[key]:key for key in MIME2FORMAT}

# file size units
KB = 1  * 10**3
MB = KB * 10**3
GB = MB * 10**3