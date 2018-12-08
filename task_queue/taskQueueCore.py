# pylint: disable=E0611,E0401
""" task queue core, without api """

from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from Task import Task, Status
from utils import extractVersions
import datetime
from google.appengine.api import urlfetch

def get_task(id):
  """ get a task by id
  
  Arguments:
    id {string} -- the id for the task
  
  Raises:
    IndexError -- If the given id is invalid / does not exist in the queue
  
  Returns:
    Task -- the task
  """

  try:
    task = ndb.Key(urlsafe=id).get()
  except (ProtocolBufferDecodeError, TypeError):
    raise TaskNotFoudError(id)
  
  if not task:
    raise TaskNotFoudError(id)
  return task

def append_task(task):
  """ append a task to the queue
  
  Arguments:
    task {Task} -- the task to be added
  
  Returns:
    string -- The id of the task
  """

  key = task.put()
  return key.urlsafe()

def update_task(id, data):
  """ Update a task with the values in 'data. Allows updating multiple
  properties at once.
  There are some limitations on what properties can be updated, when they can be
  set, and what value they can be set to.
  
  Arguments:
    id {string} -- the task id
    data {dict} -- a dictionnary with the values to update with
  
  Raises:
    KeyError -- If some of the properties in 'data' are not editable, or do not exist
    NotAllowed -- If the requested edits are not allowed in the current state of the task
    TypeError -- if a value does not have the expected type
  """

  modified = False
  # The task properties that can be accessed by this method.
  PUBLIC_PROPERTIES = set(["status", "response"])
  # properties not in PUBLIC_PROPERTIES are invalid
  invalid_properties = [prop for prop in data if prop not in PUBLIC_PROPERTIES]

  if len(invalid_properties) > 0:
    raise KeyError("Some properties are not editable, or do not exist: [{}]".format(', '.join(invalid_properties)))

  task = get_task(id)
  
  if "status" in data:
    if (task.status not in [Status.PENDING, Status.RUNNING]):
      raise NotAllowed("Status can only be set on 'active' tasks (either pending or running). To re-start a task, duplicate it")
    
    newStatus = Status(data["status"])
    if newStatus != task.status:
      task.status = newStatus
      modified = True

  if "response" in data:
    if data["response"] != task.response:
      task.response = data["response"]
      modified = True

  if modified:
    notify_task(task)
    task.put()

  return task

def notify_task(task):
  """ If the given task contains a 'callback url', call that url with the task
  as a payload """
  if (task.callback_url):
    urlfetch.fetch(
      url=task.callback_url,
      method=urlfetch.POST,
      payload=task.serialize())

def duplicate_task(id):
  """ duplicates a task and returns the new one
  
  Arguments:
    id {string} -- the id of the task to duplicate
  
  Returns:
    Task -- the dupliacted task
  """
  task = get_task(id)
  newTask = Task(
      payload=task.payload,
      tags=task.tags,
      max_attempts=task.max_attempts,
      callback_url=task.callback_url)
  newTask.put()
  return newTask

# TODO: Make this transactionnal. Now, If a lease request is received before the
# previous request has updated its task status, the same task will be returned.
# This works for now, as we have a small number of render nodes, making
# collisions unlikely
def lease_task(tags=None, lease_duration=30):
  # initialize the query
  query = Task.query()

  # We also retrieve running tasks, so that we can check if their lease is
  # expired
  query = query.filter(ndb.OR(
    Task.status == Status.PENDING,
    Task.status == Status.RUNNING,
  ))

  # filter tags
  if tags:
    query = query.filter(Task.tags.IN(tags))

  # run the query
  query = query.order(Task.create_time)
  tasks = query.fetch()

  # update all PENDING and RUNNING task status
  update_tasks(tasks)
  # Now that the statuses are updated, we can rely on them to filter tasks
  pending_tasks = [task for task in tasks if task.status == Status.PENDING]

  if pending_tasks:
    task = pending_tasks[0]

    # set task's lease_timeout
    delta = datetime.timedelta(0, lease_duration)
    task.lease_timeout = datetime.datetime.now() + delta

    # update task status
    task.status = Status.RUNNING
    task.attempt_count += 1
    task.put()

    return task
  else:
    return None

def cancel_task(id):
  update_task(id, {'status':'CANCELLED'})

def release_task(id):
  update_task(id, {'status':'PENDING'})

def update_tasks(task_list):
  updated_tasks = []

  for task in task_list:
    is_expired = task.lease_timeout and datetime.datetime.now() > task.lease_timeout
    is_modified = False

    # set tasks whose lease has expired back to pending status
    if is_expired and (task.status in [Status.PENDING, Status.RUNNING]):
      task.status = Status.PENDING
      is_modified = True

    # pending tasks that don't have any more attempts have failed
    if task.status == Status.PENDING and task.attempt_count >= task.max_attempts:
      task.status = Status.FAILED
      print "modified b"
      is_modified = True
    
    if is_modified:
      updated_tasks.append(task)
      notify_task(task)
  
  ndb.put_multi(updated_tasks)

def list_tasks():
  tasks = Task \
    .query() \
    .order(Task.create_time) \
    .fetch()
  update_tasks(tasks)
  return tasks

class TaskNotFoudError(Exception):
  pass
class NotAllowed(Exception):
  pass