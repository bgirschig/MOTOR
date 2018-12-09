# pylint: disable=E0611,E0401

# standard imports
import webapp2
# handlers
from mailHandler import MailRequestHandler
from taskCallbackHandler import TaskCallbackHandler
from frontendHandlers import ResultsPage
# google stuff
from google.appengine.api.modules.modules import get_current_module_name

# TODO: use cloud endpoints for managing user limits, monitoring, etc...
# TODO: move render nodes to gcloud compute engine

class MainPage(webapp2.RequestHandler):
	def get(self):
		service_name = get_current_module_name()
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write(service_name + ' ok')

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/task_callback', TaskCallbackHandler),
	MailRequestHandler.mapping(),
	webapp2.Route(r'/results/<request_id>', handler=ResultsPage, methods=['GET']),
], debug=True)