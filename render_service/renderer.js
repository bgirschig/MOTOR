// TODO: a more sensible approach to error handling: don't try to encode if
// render failed, don't try to upload if encode failed, etc...

const path = require("path");
const fs = require('fs-extra')
const spawn = require('child_process').spawn;
const runEncoders = require('./encodersRunner');
const global_config = require("./config");
const {Storage} = require('@google-cloud/storage');
const prepareRender = require('./prepareRender');

storage = new Storage();
// const RENDER_TEMPS_DIR = path.resolve('./render_tmps');
// const TEMPLATES_DIR = path.resolve('./templates');
// const DEFAULT_COMP_NAME = 'main';
// const REMOTE_OUTPUT_DIR = 'render_outputs'

// const isWin = process.platform === "win32";
// const aerender = isWin ? config.ae_render : config.ae_render_osx;

// let busy = false;

class Renderer {
  constructor(config={}) {
    config = Object.assign({
      "render_temps_dir": path.resolve('./render_tmps'),
      "templates_dir": path.resolve('./templates'),
      "default_comp_name": 'main',
      "remote_output_dir": 'render_outputs',
    }, config);
    this.config = config;
    
    let isWin = process.platform === "win32";
    this.aerender_cmd = isWin ? global_config.ae_render : global_config.ae_render_osx;
    
    this.busy = false;
  }

  async render(request, logger) {
    this.logger = logger;
    const renderProjectDir = path.join(this.config.render_temps_dir, request.id);
    const templateFilePath = path.join(renderProjectDir, 'template.aep');
    try {
      if(this.busy) {
        logger.warn('rejected render: the renderer was busy');
        return;
      }
      this.busy = true;

      let outputDir = await prepareRender(request, renderProjectDir,
          this.config.render_temps_dir, this.config.templates_dir, logger);
      let losslessFile = path.join(outputDir, 'lossless');
      let compName = request.compName || this.config.default_comp_name;
      
      await this.ae_render(templateFilePath, losslessFile, compName);
      logger.info('ae_render finished');
      
      // find the lossless file (after effects replaces the extension
      // depending on the environment, so we can't know)
      let losslessFiles = await findFiles(outputDir, 'lossless');
      if (losslessFiles.length === 0) throw new Error('rendered file not found');
      if (losslessFiles.length > 1) throw new Error('more than one rendered file found');
      losslessFile = losslessFiles[0];
  
      await runEncoders(losslessFile, request.encoders, logger);
      await fs.remove(losslessFile);
      let realCount = await cout_files(outputDir);
      let expectedCount = request.encoders.length;
      if (realCount != expectedCount){
        throw new Error(`Expected ${expectedCount}, found ${realCount} encoded files`);
      }
      await this.upload_renders(outputDir, request.id, request.clientID);
      
      logger.info('cleanup');
      await fs.remove(renderProjectDir);
      
      logger.info('done');
      this.busy = false;
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
    }, `spawn process: ${this.aerender_cmd + args.join(' ')}`);
  
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
      const remote_filename = this.config.remote_output_dir +"/"+ target +"/"+ filename;
      const remoteFile = storage
        .bucket(global_config.render_outputs_bucket)
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

async function cout_files(dir) {
  return fs.readdir(dir).then((files)=>{
    return files.length;
  })
}

/**
 * Returns all the files whose name mathes the given one (equivalent of <dir>/<name>.*)
 * @param {string} name The name of the file(s) to match, without extension
 */
async function findFiles(dir, name) {
  let files = await fs.readdir(dir);
  matched = files.filter(file => path.parse(file).name === name);
  matched = matched.map(file=>path.join(dir, file));
  return matched;
}

async function test(){
  
}
test();

module.exports = Renderer;
