const path = require("path");
const config = require("./config");
const spawn = require('child_process').spawn;

function runEncoders (source, encoders, logger) {
    logger.info('encoding')
    
    let promises = [];
    let dirname = path.dirname(source);

    // for each encoder, enqueue a job, and add its promise to the list
    for (let encoder of encoders) {
        console.log(encoder);
        argString = `-y -i ${source} ${encoder}`
        promises.push(ffmpeg(
            path.resolve(source),
            argString,
            {cwd:dirname, logger: logger}
        ));
    }

    // Wait for all jobs to complete.
    return Promise.all(promises);
}

async function ffmpeg(source, argString, options={}) {
    options.logger.info(`spawn process: ffmpeg ${argString}`);

    let args = argString.split(' ');
    var ffmpeg = spawn('ffmpeg', args, options);
    
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