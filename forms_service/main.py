# pylint: disable=E0611,E0401

import webapp2
from google.appengine.api.modules.modules import get_current_module_name
import jinja2
import yaml
from os import path
from formHandler import FormHandler

SERVICE_NAME = get_current_module_name()
TEMPLATES_PATH = "form_templates"

jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_PATH),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ShowForm(webapp2.RequestHandler):
  def get(self, form_name):
    with open(path.join("form_definitions", form_name+".yaml"), 'r') as f:
      form_definition = yaml.load(f)
    
    for field in form_definition["fields"]:
      if "constraints" not in field:
        field["constraints"] = {}

    print form_definition["title"]
    response = jinja.get_template(form_definition["template"]+".html").render(form_definition)
    
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(response)

class FormResponse(webapp2.RequestHandler):
  def get(self, form_name):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write('ok')

class TestRoute(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(SERVICE_NAME + ' ok')

app = webapp2.WSGIApplication([
    ('/response', FormHandler),
    ('/', TestRoute),
    webapp2.Route(r'/<form_name>', handler=ShowForm),
])