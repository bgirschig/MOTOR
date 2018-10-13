from google.appengine.api import taskqueue
import webapp2
from google.appengine.api.modules.modules import get_current_module_name
import json
from google.cloud import pubsub_v1

render_queue = taskqueue.Queue('render-queue')

"""The maximum render duration in seconds"""
MAX_RENDER_DURATION = 3600

class TestRoute(webapp2.RequestHandler):
    def get(self):
      service_name = get_current_module_name()
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write(service_name + ' ok')

class Render(webapp2.RequestHandler):
    def get(self):
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('ok')
    def post(self):
      data = json.loads(self.request.body)

      # check request, reject if invalid

      task = taskqueue.Task(payload=json.dumps(data), method='PULL')
      render_queue.add(task)

      self.response.headers['Content-Type'] = 'application/json'
      self.response.write(json.dumps(data))

class LeaseTask(webapp2.RequestHandler):
    def get(self):
      service_name = get_current_module_name()

      render_queue.lease_tasks(MAX_RENDER_DURATION, )
      self.response.headers['Content-Type'] = 'application/json'
      self.response.write(service_name + ' ok')

app = webapp2.WSGIApplication([
    ('/', TestRoute),
    ('/render', Render),
    ('/lease_task', LeaseTask),
], debug=True)