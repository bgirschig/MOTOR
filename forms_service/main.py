# pylint: disable=E0611,E0401

import webapp2
from google.appengine.api.modules.modules import get_current_module_name
import jinja2
import yaml
from os import path
from formHandler import FormHandler
from google.appengine.api import users
import logging
import traceback

SERVICE_NAME = get_current_module_name()
TEMPLATES_PATH = "form_templates"

jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_PATH),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ShowForm(webapp2.RequestHandler):
  def get(self, form_name):
    user = users.get_current_user()
    is_admin = users.is_current_user_admin()

    try:
      definition_path = path.join("form_definitions", form_name+".yaml")
      with open(definition_path, 'r') as f:
        form_definition = yaml.load(f)
    except IOError:
      self.response.set_status(404)
      return
    
    for field in form_definition["fields"]:
      if "constraints" not in field:
        field["constraints"] = {}

    # we'll want to display a logout url somewhere in our form
    form_definition["logout_url"] = users.create_logout_url('/'+form_name)

    # A reference to the form definition will be used while parsing the form
    form_definition["form_definition"] = definition_path

    if user.email() in form_definition["users"] or is_admin:
      response = jinja.get_template(form_definition["template"]+".html").render(form_definition)
      self.response.headers['Content-Type'] = 'text/html'
      self.response.write(response)
    else:
      self.response.set_status(401)
      self.response.write("you do not have access to this resource")
      return


class FormResponse(webapp2.RequestHandler):
  def get(self, form_name):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write('ok')

class Logout(webapp2.RequestHandler):
  def get(self, form_name):
    user = users.get_current_user()
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write('ok')

class TestRoute(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(SERVICE_NAME + ' ok')

def handle_500(request, response, exception):
  user = users.get_current_user()
  is_admin = users.is_current_user_admin()
  if is_admin or user.email() == "test@example.com":
    response.write("<style>html{background-color:#ddd;} .red{color:red}</style>")
    response.write("<p><strong>Note</strong> You are seeing this because you are logged in as admin</p>")
    response.write("<p class='red'>%s</p>"%exception)
    response.write("<pre>%s</pre>"%traceback.format_exc())
    logging.exception(exception)
  else:
    response.write('A server error occurred!')
    response.set_status(500)

def handle_404(request, response, exception):
  response.write("Sorry, the page you are looking for does not exist")
  response.set_status(404)

app = webapp2.WSGIApplication([
    ('/logout', Logout),
    ('/response', FormHandler),
    ('/', TestRoute),
    webapp2.Route(r'/<form_name>', handler=ShowForm),
])
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500