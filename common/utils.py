""" various utilities, too small to justify their own module """

MIME2FORMAT = {
  "image/jpeg": "JPEG",
  "image/jpg": "JPEG",
  "image/png": "PNG",
  "image/bmp": "BMP",
  "image/gif": "GIF",
  "image/tiff": "TIFF",
  "image/webp": 'WebP'
}
FORMAT2MIME = {MIME2FORMAT[key]:key for key in MIME2FORMAT}

# file size units
KB = 1  * 10**3
MB = KB * 10**3
GB = MB * 10**3