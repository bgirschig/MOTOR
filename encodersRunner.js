const ame_webservice = require('./third_party/adobe-media-encoder-webservice');
const path = require("path");
const config = require("./config");

var ame = new ame_webservice.AdobeMediaEncoder(config.media_encoder);

function runEncoders (source, encoders) {
    return ame.start()
    .then(()=>{
        let jobPromises = [];
        let dirname = path.dirname(source);

        console.log('output to ', dirname);

        // for each encoder, enqueue a job, and add its promise to the list
        for (let encoder of encoders) {
            jobPromises.push(new Promise((resolve, reject)=>{
                let presetPath = path.join(
                    config.presets_dir, encoder.presetName + '.epr');
                let destPath = path.join(dirname, encoder.filename);

                let job = ame.enqueueJob({
                    sourceFilePath: path.resolve(source),
                    destinationPath: path.resolve(destPath),
                    sourcePresetPath: path.resolve(presetPath),
                });

                job.on('progress', ()=>{
                    console.log('progress: ', job.statusText, job.progress, job.statusDetail);
                });

                job.on('ended', ()=>{
                    resolve(job.status, job.lastStatusResponse);
                });
            }));
        }

        // Wait for all jobs to complete.
        return Promise.all(jobPromises);
    })
}

module.exports = runEncoders;