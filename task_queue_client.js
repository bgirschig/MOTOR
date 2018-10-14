const fetch = require('node-fetch');
const URL = require('url').URL;
var querystring = require("querystring");

/**
 * An enum representing a task's status
 * @typedef {('PENDING'|'RUNNING'|'DONE'|'FAILED')} Status
 */

/**
 * An object representing a task
 * @typedef {Object} Task
 * @property {Status} status - the current status of the task
 * @property {Number} create_time - the timestamp for when the task was created
 * @property {Object} payload - the payload for the task
 * @property {Object} response - the response for the task (should be empty on lease)
 * @property {String[]} tags - a list of arbitrary string tags
 * @property {String} api_version - the api version: major.minor.patch
 * @property {String} key - the key (=id) of the task
 * @property {String} attempt_count - number of times this task has already been attempted
 * @property {String} max_attempts - max number of attempts for the task before declaring it 'FAILED'
 * @property {Number} lease_timeout - The timestamp when the current lease will expire
 * @property {String} lease_timeout_str - A human-readable version of the lease_timeout property
 * 
 */

class TaskQueue{
  constructor(api_url) {
    this.api_url = api_url;
  }

  /**
   * returns the list of tasks (filters will be added later)
   * @return {Task[]} the list of tasks */
  async list() {
    let url = new URL(this.api_url)
    url.pathname = "/list";

    let response = await fetch(url, {method: 'GET'});
    let data = await response.json();
    
    if (response.status != 200) {
      throw new Error(JSON.stringify(data));
    } else {
      return data;
    }
  }

  /**
   * 
   * @param {Number} lease_duration - duration in seconds before the task is
   *      re-added to the queue (if not marked as 'DONE'). Set to None for the
   *      API default value
   * @param {String[]} tags - A list of tags to filter the tasks. Set to None
   *      for the API default value
   * @returns {Task} The leased task, or null if none is available
   */
  async lease(lease_duration=null, tags=null){
    let url = new URL(this.api_url)
    url.pathname = "/lease";
    if(tags) url.searchParams.set('tags', tags.join(','));
    if(lease_duration) url.searchParams.set('lease_duration', lease_duration);

    let response = await fetch(url, {method:'GET'});

    if (response.status == 204) {
      return null;
    } else if (response.status == 200) {
      return await response.json();
    } else {
      throw new Error(await response.text());
    }
  }

  /**
   * Get a specific task
   * @param {String} task_id - the ID of the task
   * @returns {Task} the task information
   */
  async getTask(task_id) {
    let url = new URL(this.api_url)
    url.pathname = "/task/"+task_id;

    let response = await fetch(url, {method:'GET'});

    if (response.status == 200) {
      return await response.json();
    } else {
      throw new Error(await response.text());
    }
  }

  /**
   * Creates a task and appends it to the queue
   * @param {Object} payload - the payload for the task
   * @param {String[]} tags - a list of arbitrary string tags
   * @param {Number} max_attempts - max number of attempts for the task before declaring it 'FAILED'
   * @returns {String} - the created Task's key
   */
  async appendTask(payload=null, tags=null, max_attempts=null) {
    let url = new URL(this.api_url)
    url.pathname = "/task";

    let request_data = {};
    if(payload!=null) request_data["payload"] = payload;
    if(tags!=null) request_data["tags"] = tags;
    if(max_attempts!=null) request_data["max_attempts"] = max_attempts;

    let response = await fetch(url, {
      method:'POST',
      body: JSON.stringify(request_data)
    });

    if (response.status == 200) {
      let data = await response.json();
      return data.task_key;
    } else {
      throw new Error(await response.text());
    }
  }

  /**
   * Updates a task. Note that only some of the task's properties can be changed
   *  - status
   *  - response
   * @param {Task} task - The task to be updated, with its modified properties
   */
  async updateTask(task) {
    let url = new URL(this.api_url)
    url.pathname = "/task/"+task.key;

    let request_data = {};
    request_data.status = task.status;
    request_data.response = task.response;

    let response = await fetch(url, {
      method:'PUT',
      body: JSON.stringify(request_data)
    });

    if (response.status == 200) {
      return await response.json();
    } else {
      throw new Error(await response.text());
    }
  }
}

module.exports = TaskQueue