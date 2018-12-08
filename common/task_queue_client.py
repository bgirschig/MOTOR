# pylint: disable=E0611,E0401

import logging
from google.appengine.api import urlfetch
import json
from os import path
import urllib
from google.appengine.api.modules.modules import get_hostname

default_api_url = "http://{}".format(get_hostname('task-queue'))
default_callback_url = "http://{}/task_callback".format(get_hostname('default'))

class Queue():
  def __init__(self, api_url=default_api_url):
    self.api_url = api_url
  
  def list(self):
    """ returns the list of tasks (filters will be added later) """
    response = urlfetch.fetch(
        url=path.join(self.api_url, 'list'),
        method=urlfetch.GET
    )
    if response.status_code != 200:
      handleError(response)
    return json.loads(response.content)

  
  def lease(self, lease_duration=None, tags=None):
    """ Lease a task from the queue
    
    Keyword Arguments:
      lease_duration {int} -- duration in seconds before the task is re-added to
          the queue (if not marked as 'DONE'). Set to None for the API default
          value
      tags {[string]} -- a list of tags to filter the tasks. Set to None for the
          API default value

    Returns:
      {dict|None} -- The leased task object, unless there are none.
    """
    params = {}
    if tags: params['tags'] = ', '.join(tags)
    if lease_duration: params['lease_duration'] = lease_duration
    param_string = urllib.urlencode(params)
    
    request_url = path.join(self.api_url, 'lease?'+param_string)

    response = urlfetch.fetch(url=request_url, method=urlfetch.GET)
    if response.status_code == 204:
      return None
    if response.status_code != 200:
      handleError(response)

    return json.loads(response.content)

  def getTask(self, task_id):
    """Returns the task object for the given ID
    
    Arguments:
      task_id {string} -- a task id
    
    Raises:
      Exception -- raised when the task id is invalid, or does not exist
    
    Returns:
      {dict} -- the task object for the given ID
    """
    response = urlfetch.fetch(
        url=path.join(self.api_url, 'task'),
        method=urlfetch.GET
    )
    if response.status_code != 200:
      handleError(response)
    return json.loads(response.content)

  def appendTask(self, payload=None, tags=None, max_attempts=None, callback_url=default_callback_url):
    """Creates a task and appends it to the queue
    
    Keyword Arguments:
      payload {dict} -- json-serializable payload for the task
      tags {[string]} -- a list of tags to itentify groups of tasks within the queue
      max_attempts {int} -- how many attempts should the task be tried before being declared 'FAILED'
      callback_url {str} -- When the task's status changes, notify this url
    
    Returns:
      {dict} -- The created Task
    """
    request_data = {}
    if payload!=None: request_data["payload"] = payload
    if tags!=None: request_data["tags"] = tags
    if max_attempts!=None: request_data["max_attempts"] = max_attempts
    if callback_url!=None: request_data["callback_url"] = callback_url
    
    response = urlfetch.fetch(
        url=path.join(self.api_url, 'task'),
        method=urlfetch.POST,
        payload=json.dumps(request_data),
    )
    if response.status_code != 200:
      handleError(response)
    return json.loads(response.content)
  
  def updateTask(self, task_id, status=None, response=None):
    """ Updates a task's properties
    
    Arguments:
      task_id {string} -- the id for the task to be modified
    
    Keyword Arguments:
      status {int} -- The status of the task
      response {dict} -- The 'response' object for the task.
    
    Returns:
      {dict} -- The modified task object
    """

    request_data = {}
    if status!=None: request_data["status"] = status
    if response!=None: request_data["response"] = response

    response = urlfetch.fetch(
        url=path.join(self.api_url, 'task', task_id),
        method=urlfetch.PUT,
        payload=json.dumps(request_data)
    )
    if response.status_code != 200:
      handleError(response)
    return json.loads(response.content)

def handleError(response):
  try:
    raise Exception(json.loads(response.content))
  except:
    raise Exception(response.content)