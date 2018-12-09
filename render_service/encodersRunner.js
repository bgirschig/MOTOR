const path = require("path");
const config = require("./config");
const spawn = require('child_process').spawn;

function runEncoders (source, encoders, logger) {
  logger = logger || console;
  logger.info('encoding')
  
  let promises = [];
  let dirname = path.dirname(source);
  dirname = path.resolve(dirname);

  // for each encoder, enqueue a job, and add its promise to the list
  for (let encoder of encoders) {
    logger.info('encoder: ', encoder);
    argString = `-y -loglevel error -i ${source} ${encoder}`
    promises.push(ffmpeg(
      argString,
      {cwd:dirname, logger: logger}
    ));
  }

  // Wait for all jobs to complete.
  return Promise.all(promises);
}

async function ffmpeg(argString, options={}) {
  let args = argString.split(' ');
  options.logger.info(`spawn process: ${process.env.FFMPEG_PATH} ${args.join(' ')}`);

  var ffmpeg = spawn(
    process.env.FFMPEG_PATH,
    args,
    options);
  
  ffmpeg.on('error', (err) => {
    options.logger.error('ffmpeg error:'+err, String(err));
  });
  ffmpeg.stdout.on('data', data => {
    options.logger.info('ffmpeg stdout: ' + data.toString().trim());
  })
  ffmpeg.stderr.on('data', (data) => {
    options.logger.error('ffmpeg stderr:', data.toString());
  });
  return new Promise((resolve, reject)=>{
    ffmpeg.on('close', function (code) {
      if (code == 0) resolve();
      else reject('ffmpeg command failed');
    });
  })
}

module.exports = runEncoders;