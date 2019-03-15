# pylint: disable=E0611,E0401

import webapp2
from google.appengine.api.modules.modules import get_current_module_name
import json
from formResponseHandler import FormResponseHandler
from google_forms import checkSpreadsheet
import formRenderer
from common import errorHandlers

class TestRoute(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(get_current_module_name() + ' ok')

class ShowForm(webapp2.RequestHandler):
  def get(self, form_name):
    form = formRenderer.render(form_name)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(form)

class CheckSpreadsheet(webapp2.RequestHandler):
  def get(self):
    spreadsheet_id = "1ki4K_Y6FPuSTY4tEJP38c_N-kIPMNH3c9JzEQcgp_UU"
    data = checkSpreadsheet(spreadsheet_id, 'xenix')

    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(data))

app = webapp2.WSGIApplication([
    ('/response', FormResponseHandler),
    ('/check_spreadsheets', CheckSpreadsheet),
    ('/', TestRoute),
    webapp2.Route(r'/<form_name>', handler=ShowForm),
])
app.error_handlers[404] = errorHandlers.handle_404
app.error_handlers[500] = errorHandlers.handle_500