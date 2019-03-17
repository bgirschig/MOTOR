# pylint: disable=E0611,E0401

""" Render forms according to form definitions """

from os import path
from google.appengine.api import users
import yaml
from common.exceptions import NotAllowed, NotFound
from jinja_config import jinja
from Form import Form

def render(form_name):
  # load the form definition
  definition = Form.query(Form.name == form_name).get()
  if not definition:
    raise NotFound('Could not find a form definition named '+form_name)
  form_definition = yaml.load(definition.content)

  # check form definition's validity
  if "users" not in form_definition:
    raise ValueError('invalid form definition (missing key "users"): '+form_name)

  # we'll want to display a logout url somewhere in our form
  form_definition["logout_url"] = users.create_logout_url('/'+form_name)
  # A reference to the form definition will be used while parsing the form
  form_definition["form_definition"] = form_name

  # find out if the user is allowed to see this ressource
  user = users.get_current_user()
  is_admin = users.is_current_user_admin()
  user_can_see = user.email() in form_definition["users"] or is_admin

  # render the form
  if user_can_see:
    template_path = form_definition["template"]+".html"
    response = jinja.get_template(template_path).render(form_definition)
    return response
  else:
    raise NotAllowed("you do not have access to this resource")