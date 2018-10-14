// Use the gcloud trace agent
// This is supposed to help combining all the logs related to a single request.
// Disabled because there is a problem with authorisations
// require('@google-cloud/trace-agent').start();

const app = require("express")();
const Renderer = require('./renderer');
const requestDefaults = require('./request_defaults');
const config = require("./config");
var bodyParser = require('body-parser');
const logger = require('./logging');
const QueueClient = require('./task_queue_client');

// load environment variables from the .env file
require('dotenv').config()

// parse json bodies
app.use(bodyParser.json());
// log basic info about all requests
app.use(logger.middleware);

// create renderer
let renderer = new Renderer();
// create queue client
let queue = new QueueClient(config.queue_api_url);

app.get('/test', (req, res) => {
  res.send('ok');
})

async function handleTask(task) {
  let request_logger = logger.child({
    tracker: task.key
  })

  // pass down the task id to the renderer
  task.payload.id = task.key;

  request_logger.info("handleTask");

  let request = {};
  Object.assign(request, requestDefaults);
  Object.assign(request, task.payload);

  await renderer.render(request, request_logger);
  request_logger.info('completed render request');
}

async function checkQueue() {
  if (renderer.busy) return;
  let task = await queue.lease(60*10);
  if(task) {
    try {
      await handleTask(task);
      task.status = "DONE";
      await queue.updateTask(task);
    } catch (error) {
      logger.error(error);
      task.status = "PENDING";
      task.response = error;
      let updated_task = await queue.updateTask(task);
    }
    checkQueue();
  }
}
setInterval(checkQueue, config.queue_ping_rate * 1000);
checkQueue();

var env = process.env.NODE_ENV || 'dev';
app.listen(config.apiPort, '0.0.0.0', () => {
  if (env === 'production') logger.info(`service (re)started on port ${config.apiPort}!`)
})