# pylint: disable=E0611,E0401

import logging
import webapp2
from google.appengine.api.modules.modules import get_current_module_name
from Task import Task
import json
from google.appengine.ext import ndb
from google.appengine.ext.db import BadValueError
import datetime
from jinja_setup import jinja
import taskQueueCore
import errorHandlers

ndb.get_context().set_cache_policy(lambda key: False)

class ServiceTest(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(get_current_module_name() + ' ok')

class TaskHandler(webapp2.RequestHandler):
  def get(self, task_key):
    task = taskQueueCore.get_task(task_key)
    data = task.toDict()
    if self.request.url.endswith(".html"):
      data["payload"] = json.dumps(data["payload"], indent=2)
      html = jinja.get_template('task.html').render(data)
      self.response.headers['Content-Type'] = 'text/html'
      self.response.write(html)
    else:
      self.response.headers['Content-Type'] = 'application/json'
      self.response.write(json.dumps(data))

  def post(self):
    try:
      request_data = json.loads(self.request.body)
    except ValueError as error:
      raise ValueError("Json parsing error: "+str(error))

    try:
      task = Task(
        payload=request_data.get("payload", {}),
        tags=request_data.get("tags", []),
        max_attempts=request_data.get("max_attempts", 5),
        callback_url=request_data.get("callback_url", ""))
    except BadValueError as error:
      raise ValueError("Invalid task data: "+str(error))

    task_id = taskQueueCore.append_task(task)
    self.response.headers['Content-Type'] = 'application/json'

    self.response.status = 200
    self.response.write(json.dumps({
      'message': 'successfully inserted task into queue',
      'task_key': task_id,
    }))

  def put(self, task_key):
    try:
      request_data = json.loads(self.request.body)
    except ValueError as error:
      raise ValueError("Json parsing error: "+error)

    task = taskQueueCore.update_task(task_key, request_data)

    self.response.status = 200
    self.response.write(task.serialize())

class DuplicateHandler(webapp2.RequestHandler):
  def get(self, task_key):
    taskQueueCore.duplicate_task(task_key)
    self.redirect("/list.html")

class CancelHandler(webapp2.RequestHandler):
  def get(self, task_key):
    taskQueueCore.cancel_task(task_key)
    self.redirect("/list.html")

class FailHandler(webapp2.RequestHandler):
  def get(self, task_key):
    taskQueueCore.release_task(task_key)
    self.redirect("/list.html")

class ListHandler(webapp2.RequestHandler):
  def get(self):
    tasks = taskQueueCore.list_tasks()
    tasks = [task.toDict() for task in tasks]
    if self.request.url.endswith(".html"):
      html = jinja.get_template('queue.html').render({"tasks": tasks})
      self.response.headers['Content-Type'] = 'text/html'
      self.response.write(html)
    else:
      self.response.headers['Content-Type'] = 'application/json'
      self.response.write(json.dumps(tasks))

class LeaseHandler(webapp2.RequestHandler):
  def get(self):
    # get tags from request
    tags = self.request.GET.get("tags", "")
    tags = tags.split(",") if tags else None
    # get lease duration from request
    lease_duration = self.request.GET.get('lease_duration', 30)
    lease_duration = int(lease_duration)

    task = taskQueueCore.lease_task(tags, lease_duration)
    if task:
      self.response.headers['Content-Type'] = 'application/json'
      self.response.write(task.serialize())
    else:
      self.response.write("There are no tasks to be leased")
      self.response.status = 204

app = webapp2.WSGIApplication([
    ('/', ServiceTest),
    webapp2.Route(r'/task/<task_key>.html', handler=TaskHandler, methods=['GET']),
    webapp2.Route(r'/task/<task_key>', handler=TaskHandler, methods=['GET', 'PUT']),
    webapp2.Route(r'/task', handler=TaskHandler, methods=['POST']),
    webapp2.Route(r'/duplicate/<task_key>', handler=DuplicateHandler, methods=['GET']),
    webapp2.Route(r'/cancel/<task_key>', handler=CancelHandler, methods=['GET']),
    webapp2.Route(r'/fail/<task_key>', handler=FailHandler, methods=['GET']),
    webapp2.Route(r'/list.html', handler=ListHandler, methods=['GET']),
    webapp2.Route(r'/list', handler=ListHandler, methods=['GET']),
    webapp2.Route(r'/lease', handler=LeaseHandler, methods=['GET']),
], debug=True)
app.error_handlers[404] = errorHandlers.handle_404
app.error_handlers[500] = errorHandlers.handle_500