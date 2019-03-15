""" utilities for file-like objects (not io/filesystem operations) """

import math
from common.exceptions import FileSizeExceeded

def isFile(item):
  """ returns true if the given item is a file """
  try:
    return bool(item.file)
  except AttributeError:
    return False

def get_file_size(file):
  """ returns the size of the given file in bytes """
  file.seek(0, 2)
  size = file.tell()
  file.seek(0)
  return size

def checkFile_size(file, max_size_bytes, file_name='no name'):
  """ checks if the given file is smaller than max_size_bytes. raises
  FileSizeExceeded otherwise """
  file_size = get_file_size(file)
  if file_size > max_size_bytes:
    human_max_size = str(math.floor(max_size_bytes/1000))+"KB"
    human_size = str(math.floor(file_size/1000))+"KB"
    
    message = ("The file '{file_name}' ({file_size}) exceeds the allowed "
      "{max_size} file size").format(
      file_name=file_name, file_size=human_size, max_size=human_max_size)
    raise FileSizeExceeded(message)