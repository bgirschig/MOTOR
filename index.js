// Use the gcloud trace agent
// This is supposed to help combining all the logs related to a single request.
// Disabled because there is a problem with authorisations
// require('@google-cloud/trace-agent').start();

const express = require("express");
const renderer = require('./renderer');
const requestDefaults = require('./request_defaults');
const config = require("./config");
var bodyParser = require('body-parser');
const logger = require('./logging');


// load environment variables from the .env file
require('dotenv').config()

const app = express();

app.use(bodyParser.json());

// log basic info about all requests
app.use(logger.middleware);

app.get('/test', (req, res) => {
  res.send('ok');
})

app.post('/render', (req, res) => {
  let request = {};
  Object.assign(request, requestDefaults);
  Object.assign(request, req.body);

  renderer(request, req.logger)

  res.send(`http://motor.bastiengirschig.com/render_outputs/${request.id}`);
})

var env = process.env.NODE_ENV || 'dev';
app.listen(config.apiPort, '0.0.0.0', () => {
  if (env === 'production') logger.info(`service (re)started on port ${config.apiPort}!`)
})