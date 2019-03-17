import webapp2
from google.appengine.api import users
import re

""" Wrapper for our API methods (manages login, CORS, etc...)
Usage example:
class DefinitonsHandler(HandlerWrapper):
  # The constructor can be used to set some options for the wrapper
  def __init__(self, request, response):
    super(DefinitonsHandler, self).__init__(request, response)
    self.login = 'public'

  def put(self, form_name):
    self.response.write('yep')
"""

class HandlerWrapper(webapp2.RequestHandler):
  def __init__(self, request, response):
    super(HandlerWrapper, self).__init__(request, response)

    self.allowed_origins = [
      r'http://localhost(:\d{2,})?$', # localhost, any port
      r'https://\w+-dot-kairos-motor.appspot.com' # all services in kairos-motor
    ]
    self.allowed_methods = 'GET, PUT, POST, OPTIONS'
    self.content_type = 'application/json'
    # login mode: either 'admin', 'user', or 'public'
    self.login = 'admin'
    # When authentication fails, should we return a 403, or send a redirect to
    # the login page
    self.redirect_to_login = False

  def dispatch(self):
    # set the Allow-Origin header.
    if self.request.headers.has_key('origin') and match_origin(self.request.headers['Origin'], self.allowed_origins):
      self.response.headers['Access-Control-Allow-Origin'] = self.request.headers['Origin']

    # set other headers
    self.response.headers['Access-Control-Allow-Methods'] = self.allowed_methods
    self.response.headers['Content-Type'] = self.content_type
    self.response.headers['Access-Control-Allow-Credentials'] = 'true'

    # Handle preflight requests: Never require a login.
    if self.request.method == "OPTIONS":
      # For some reason, the following line raises a '405 (Method Not Allowed)'
      # error, so we just skip the dispatch and it works.
      # super(HandlerWrapper, self).dispatch()
      return

    # Handle regular requests
    user = users.get_current_user()
    if self.login == 'admin' and not users.is_current_user_admin():
      self.handle_auth_fail()
    elif self.login == 'user' and not user:
      self.handle_auth_fail()
    else:
      super(HandlerWrapper, self).dispatch()

  def handle_auth_fail(self):
    if self.redirect_to_login:
      login_url = users.create_login_url(self.request.url)
      self.redirect(login_url)
    else:
      self.abort(403)

def match_origin(origin, allowed_origins):
  for pattern in allowed_origins:
    if re.match(pattern, origin): return True
  return False
