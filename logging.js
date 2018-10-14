const bunyan = require('bunyan');
const {LoggingBunyan} = require('@google-cloud/logging-bunyan');
const colors = require('colors');
const uuidv1 = require('uuid/v1');

const colorMap = {
  "fatal": "inverse",
  "error": "red",
  "warn": "yellow",
  "info": "cyan",
  "debug": "grey",
  "trace": "magenta",
}

const stdoutSerializer = {
  write(rec) {
    let loglevel = bunyan.nameFromLevel[rec.level];
    let logColor = colorMap[loglevel];
    console.log('[%s][%s][%s]: %s',
      rec.time.toISOString(),
      rec.tracker || '',
      colors.bold(colors[logColor](loglevel)),
      rec.msg,
    );
  }
}

const loggingBunyan = new LoggingBunyan();
// main logger for the render service
const logger = bunyan.createLogger({
  name: 'render-service',
  streams: [
    {stream: stdoutSerializer, level: 'info', type: 'raw'},
    loggingBunyan.stream('info'),
  ],
});

logger.middleware = function(req, res, next) {
  let tracker = req.body.tracker || req.body.id || uuidv1();
  req.body.tracker = tracker;

  req.logger = logger.child({
    tracker: tracker,
    parent: req.originalUrl,
  })

  // TODO: add other information (requester IP, etc...)
  req.logger.info({
    body: req.body,
    method: req.method,
  }, `[${req.method}] ${req.originalUrl}`)
  next();
}

module.exports = logger;