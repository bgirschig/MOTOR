# pylint: disable=E0611,E0401

import webapp2
from google.appengine.api.modules.modules import get_current_module_name
import json
from formResponseHandler import FormResponseHandler
from google_forms import checkSpreadsheet
import formRenderer
from common import errorHandlers
from DefinitionsHandler import DefinitonsHandler, DefinitonsList
from common.api_utils import HandlerWrapper

class TestRoute(HandlerWrapper):
  def __init__(self, request, response):
    super(TestRoute, self).__init__(request, response)
    self.login = 'public'

  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(get_current_module_name() + ' ok')

class ShowForm(HandlerWrapper):
  def __init__(self, request, response):
    super(ShowForm, self).__init__(request, response)
    self.login = 'user'
    self.redirect_to_login = True
    self.content_type = 'text/html'

  def get(self, form_name):
    form = formRenderer.render(form_name, self)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(form)

class CheckSpreadsheet(HandlerWrapper):
  def get(self):
    spreadsheet_id = "1ki4K_Y6FPuSTY4tEJP38c_N-kIPMNH3c9JzEQcgp_UU"
    data = checkSpreadsheet(spreadsheet_id, 'xenix')

    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(data))

app = webapp2.WSGIApplication([
    webapp2.Route(r'/api/definitions', handler=DefinitonsList),
    webapp2.Route(r'/api/definition/<form_name>', handler=DefinitonsHandler),
    ('/response', FormResponseHandler),
    ('/check_spreadsheets', CheckSpreadsheet),
    ('/', TestRoute),
    webapp2.Route(r'/<form_name>', handler=ShowForm),
])
app.error_handlers[404] = errorHandlers.handle_404
app.error_handlers[500] = errorHandlers.handle_500