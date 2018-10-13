""" extracts major, minor and patch versions from a version string
Returns:
  [int] -- major version number
  [int] -- minor version number
  [int] -- patch number
"""
def extractVersions(version_string):
  return [int(val) for val in version_string.split('.')]