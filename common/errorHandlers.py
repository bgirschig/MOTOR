# pylint: disable=E0611,E0401

import logging
import traceback
from google.appengine.api import users
import jinja2
from common import exceptions
from os.path import join as joinpath
from os.path import dirname

# jinja config
jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(joinpath(dirname(__file__),"templates")),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def handle_500(request, response, exception):
  logging.exception(exception)
  is_admin = users.is_current_user_admin()
  
  info = {
    'message': '',
    'is_admin': is_admin,
    'traceback': traceback.format_exc(),
  }

  if isinstance(exception, exceptions.ClientException):
    response.set_status(400)
    # For a client exception, always log the detailed message
    info['message'] = exception.message
  else:
    response.set_status(500)
    # For a non-client exception, log a generic message to non admin users
    info['message'] = exception.message if is_admin else "An unexpected error occurred"
  
  html = jinja.get_template('error.html').render(info)
  response.write(html)

def handle_404(request, response, exception):
  is_admin = users.is_current_user_admin()
  response.write("Sorry, the ressource you are looking for does not exist")
  if is_admin:
    response.write(exception)
    response.write(traceback.format_exc())
  response.set_status(404)