import webapp2
from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from common.exceptions import NotFound, InvalidYaml
from common.api_utils import HandlerWrapper
from Form import Form
import yaml
import json

class DefinitonsHandler(HandlerWrapper):
  def __init__(self, request, response):
    super(DefinitonsHandler, self).__init__(request, response)
    self.login = 'user'

  def put(self, form_name):
    if not self.isAdmin:
      self.abort(403, 'only admin users are allowed to update forms')

    definition = Form.query(Form.name == form_name).get()
    if not definition:
      definition = Form(name=form_name, content="")

    # Ensure the uploaded doc is correct yaml
    try:
      yaml.load(self.request.body)
    except yaml.scanner.ScannerError as e:
      raise InvalidYaml(e.message)

    definition.content = self.request.body
    definition.put()

    self.response.write(definition.serialize())

  def get(self, form_name):
    definition = Form.query(Form.name == form_name).get()
    if not definition:
      self.abort(404, "There is no form with name {}".format(form_name))
    else:
      self.response.write(definition.serialize())

class DefinitonsList(HandlerWrapper):
  def get(self):
    output = [item.name for item in Form.query()]
    self.response.write(json.dumps(output))