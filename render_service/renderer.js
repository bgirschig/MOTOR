// TODO: a more sensible approach to error handling: don't try to encode if
// render failed, don't try to upload if encode failed, etc...

const path = require("path");
const fs = require('fs-extra')
const spawn = require('child_process').spawn;
const runEncoders = require('./encodersRunner');
const {Storage} = require('@google-cloud/storage');
const prepareRender = require('./prepareRender');
const config = require("./config");
const {findFiles, cout_files} = require('./fileUtils');

storage = new Storage();

class Renderer {
  constructor() {
    let isWin = process.platform === "win32";
    this.aerender_cmd = isWin ? config.ae_render : config.ae_render_osx;
    
    this.busy = false;
  }

  async render(request, logger) {
    this.logger = logger;
    
    /** The tempoary folder where the template will be copied and the rendered
     * video will be created */
    const renderProjectDir = path.resolve(
      path.join(config.renderer.render_temps_dir, request.id));
    /** The after effects file within the renderProjectDir */
    const templateFilePath = path.resolve(
      path.join(renderProjectDir, 'template.aep'));
    
    try {
      if(this.busy) {
        logger.warn('rejected render: the renderer was busy');
        return;
      }
      this.busy = true;
      
      // create the output directory.
      const outputDir = path.resolve(path.join(renderProjectDir, 'output'));
      await fs.ensureDir(outputDir);

      // prepare the reder dir: update template, create temp dir, download resources, ...
      await prepareRender(request, renderProjectDir, logger);
      
      // Do the actual rendering
      let losslessFile = path.join(outputDir, 'lossless');
      let compName = request.compName || "main";
      await this.ae_render(templateFilePath, losslessFile, compName);
      logger.info('ae_render finished');
      
      // find the lossless file (after effects replaces the extension
      // depending on the environment, so we can't know)
      let losslessFiles = await findFiles(outputDir, 'lossless');
      if (losslessFiles.length === 0) throw new Error('rendered file not found');
      if (losslessFiles.length > 1) throw new Error('more than one rendered file found');
      losslessFile = losslessFiles[0];
  
      // convert the video to the various formats required
      await runEncoders(losslessFile, request.encoders, logger);
      // remove the now useless lossless file
      await fs.remove(losslessFile);
      // check if the encoders worked properly
      let realCount = await cout_files(outputDir);
      let expectedCount = request.encoders.length;
      if (realCount != expectedCount){
        throw new Error(`Expected ${expectedCount}, found ${realCount} encoded files`);
      }

      logger.info('uploading rendered files to storage');
      await this.upload_renders(outputDir, request.id, request.clientID);
      
      logger.info('cleanup');
      await fs.remove(renderProjectDir);
      
      this.busy = false;
      logger.info('done');
    } catch (err) {
      logger.info('cleanup after error: ', err.message);
      await fs.remove(renderProjectDir);
      
      this.busy = false;
      throw err;
    }
  }

  async ae_render(templateFilePath, losslessFile, compName) {
    let args = [
      '-project', templateFilePath,
      '-comp', compName,
      '-output', losslessFile,
      '-continueOnMissingFootage',
    ];
  
    this.logger.info({
      command:{
        'command-path': this.aerender_cmd,
        'args': args,
      }
    }, `spawn process: ${this.aerender_cmd +" "+ args.join(' ')}`);
  
    // TODO: add a timeout
    // TODO: bundle multiple stdout lines together before sending, or only
    // debug-log them
    var ae = spawn(this.aerender_cmd, args);
    ae.stdin.end();
    ae.on('error', (err) => {
      this.logger.error(err, String(err));
    });
    ae.stdout.on('data', data => {
      this.logger.info('stdout: ' + data.toString().trim());
    })
    ae.stderr.on('data', (data) => {
      this.logger.error('stderr:', data.toString());
    });
    return new Promise((resolve, reject)=>{
      ae.on('close', function (code) {
        if (code == 0) resolve();
        else reject('aerender command failed');
      });
    })
  }

  async upload_renders(outputDir, target, accessList="") {
    const files = await fs.readdir(outputDir);
    const promises = files.map(filename => {
      const local_filename = path.join(outputDir, filename);
      // Not using path.join here because a render node might be on windows,
      // so path.join would create path with backslashs
      const remote_filename = config.renderer.remote_output_dir +"/"+ target +"/"+ filename;
      const remoteFile = storage
        .bucket(config.render_outputs_bucket)
        .file(remote_filename);          
      const options = {metadata:{metadata:{}}};
      options.metadata.metadata.accessList = accessList;
      return new Promise((resolve, reject)=>{
        fs.createReadStream(local_filename)
          .pipe(remoteFile.createWriteStream(options))
          .on('error', reject)
          .on('finish', resolve);
      });
    });
    await Promise.all(promises);
  }
}

module.exports = Renderer;
