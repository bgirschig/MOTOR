# pylint: disable=E0611,E0401
 
import logging
import traceback
from google.appengine.api import users

def handle_500(request, response, exception):
  logging.exception(exception)
  user = users.get_current_user()
  is_admin = users.is_current_user_admin()
  if user: is_admin = is_admin or user.email() == "test@example.com"
  if is_admin:
    response.write("<style>html{background-color:#ddd;} .red{color:red}</style>")
    response.write("<p><strong>Note</strong> You are seeing this because you are logged in as admin</p>")
    response.write("<p class='red'>%s</p>"%exception)
    response.write("<pre>%s</pre>"%traceback.format_exc())
  else:
    response.write('A server error occurred!')
    response.set_status(500)

def handle_404(request, response, exception):
  response.write("Sorry, the page you are looking for does not exist")
  response.set_status(404)