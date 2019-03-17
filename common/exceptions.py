class ClientException(Exception):
  """Exceptions caused by a client misuse should inherit from this base exception
  so that the error will be reported to the client. Otherwise, the exception will
  be logged but hidden from the user (who will get a generic 500 error)"""
  pass

class FileSizeExceeded(ClientException):
  """Raised when a client tries to upload / handle a size that exceeds a limit"""
  pass

class NotFound(ClientException):
  pass

class NotAllowed(ClientException):
  pass

class InvalidYaml(ClientException):
  pass