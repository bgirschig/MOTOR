import logging
import webapp2
from google.appengine.api.modules.modules import get_current_module_name
from Task import Task, Status
import json
from utils import extractVersions
from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from google.appengine.ext.db import BadValueError
import datetime

API_VERSION = "0.0.1"
SERVICE_NAME = get_current_module_name()

current_major, current_minor, current_patch = extractVersions(API_VERSION)

class TestRoute(webapp2.RequestHandler):
    def get(self):
      self.response.headers['Content-Type'] = 'text/html'
      self.response.write(SERVICE_NAME + ' ok')

class ApiItem(webapp2.RequestHandler):
  def get(self, item_key):
    self.response.headers['Content-Type'] = 'application/json'
    try:
      item = ndb.Key(urlsafe=item_key).get()
    except ProtocolBufferDecodeError:
      self.response.write(json.dumps({ "error": "invalid key"}))
    except TypeError:
      self.response.write(json.dumps({ "error": "invalid key"}))
    else:
      self.response.write(json.dumps(item.toDict()))
    
  def post(self):
    self.response.headers['Content-Type'] = 'application/json'

    try:
      request_data = json.loads(self.request.body)
    except ValueError as error:
      errorHandler(error, "Json parsing error. Check logs for more details", self)
      return

    try:
      item = Task(payload=request_data.get("payload", {}),
          tags=request_data.get("tags", []),
          max_attempts=request_data.get("max_attempts", 5))
    except BadValueError as error:
      errorHandler(error, "Invalid request. check logs for more details", self)
      return

    key = item.put()
    self.response.status = 200
    self.response.write(json.dumps({
      'message': 'successfully inserted item into queue',
      'item_key': key.urlsafe(),
    }))
  
  def put(self, item_key):
    try:
      request_data = json.loads(self.request.body)
    except ValueError as error:
      errorHandler(error, "Json parsing error. Check logs for more details", self)
      return

    # The task properties that can be accessed by this method.
    PUBLIC_PROPERTIES = set(["status", "response"])
    # The properties defined in the put request data
    request_properties = set(request_data.keys())
    # properties not in PUBLIC_PROPERTIES are invalid
    invalid_properties = PUBLIC_PROPERTIES ^ request_properties

    if len(invalid_properties) > 0:
      msg = "Invalid request: some properties are not editable, or do not exist: [{}]".format(', '.join(invalid_properties))
      errorHandler(None, msg, self)
      return

    try:
      item = ndb.Key(urlsafe=item_key).get()
    except ProtocolBufferDecodeError:
      self.response.write(json.dumps({ "error": "invalid key"}))
    except TypeError:
      self.response.write(json.dumps({ "error": "invalid key"}))
    else:
      if "status" in request_data:
        item.status = Status(request_data["status"])
      if "response" in request_data:
        item.response = request_data["response"]

      item.put()

      self.response.status = 200
      self.response.write('ok')

    print item_key, request_data

    pass

class ApiList(webapp2.RequestHandler):
  def get(self):
    items = Task \
        .query() \
        .order(Task.create_time) \
        .fetch()
    items = [item.toDict() for item in items if hasValidApiVersion(item)]

    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(items))

# TODO: Make this transactionnal. If a lease request is received before the
# previous request has updated its task status, the same task will be returned
# This works for now, as we have a small number of render nodes, making
# collisions unlikely
class ApiLease(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'application/json'

    # initialize the query
    query = Task.query()

    # We also retrieve running tasks, so that we can check if their lease is
    # expired
    query = query.filter(ndb.OR(
      Task.status == Status.PENDING,
      Task.status == Status.RUNNING,
    ))

    # filter tags
    if "tags" in self.request.GET:
      query = query.filter(Task.tags.IN(self.request.GET["tags"]))

    # run the query
    query = query.order(Task.create_time)
    tasks = query.fetch()

    # update all PENDING AND RUNNING task status (not only the one we'll lease)
    for task in tasks:
      # set tasks whose lease has expired back to pending status
      if task.lease_timeout and datetime.datetime.now() > task.lease_timeout:
        task.status = Status.PENDING
      # pending tasks that don't have any more attempts have failed
      if task.status == Status.PENDING and task.attempt_count >= task.max_attempts:
        task.status = Status.FAILED


    # Now that the statuses are updated, we can rely on them to filter pending
    # tasks
    pending_tasks = [task for task in tasks if task.status == Status.PENDING]

    if pending_tasks:
      task = pending_tasks[0]

      # set task's lease_timeout
      lease_duration = self.request.GET.get('lease_duration', 30)
      lease_duration = int(lease_duration)
      delta = datetime.timedelta(0, lease_duration)
      task.lease_timeout = datetime.datetime.now() + delta

      # update task status
      task.status = Status.RUNNING
      task.attempt_count += 1

      self.response.write(json.dumps(task.toDict()))
    else:
      # There are no tasks to be leased
      self.response.status = 204

    ndb.put_multi(tasks)


def errorHandler(error, message, handler):
  if error: logging.error(error)
  handler.response.status = 400
  handler.response.write(json.dumps({'error': message}))

""" returns true if the item is compatible with the current api version """
def hasValidApiVersion(item):
  item_major, item_minor, _ = extractVersions(item.api_version)
  return item_major == current_major and item_minor <= current_minor

app = webapp2.WSGIApplication([
    ('/', TestRoute),
    webapp2.Route(r'/item/<item_key>', handler=ApiItem, methods=['GET', 'PUT']),
    webapp2.Route(r'/item', handler=ApiItem, methods=['POST']),
    ('/list', ApiList),
    ('/lease', ApiLease),
], debug=True)