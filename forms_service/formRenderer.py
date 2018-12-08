# pylint: disable=E0611,E0401

""" Render forms according to form definitions """

from os import path
from google.appengine.api import users
import yaml
import jinja2
from common.exceptions import NotAllowed, NotFound

jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(''),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def render(form_name):
  # get the form definition
  try:
    definition_path = path.join("form_definitions", form_name+".yaml")
    with open(definition_path, 'r') as f:
      form_definition = yaml.load(f)
  except IOError:
    raise NotFound('Could not find a form definition named '+form_name)

  # we'll want to display a logout url somewhere in our form
  form_definition["logout_url"] = users.create_logout_url('/'+form_name)
  # A reference to the form definition will be used while parsing the form
  form_definition["form_definition"] = definition_path

  # find out if the user is allowed to see this ressource
  user = users.get_current_user()
  is_admin = users.is_current_user_admin()
  user_can_see = user.email() in form_definition["users"] or is_admin

  # render the form
  if user_can_see:
    template_path = "form_templates/{}.html".format(form_definition["template"])
    response = jinja.get_template(template_path).render(form_definition)
    return response
  else:
    raise NotAllowed("you do not have access to this resource")