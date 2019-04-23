const path = require("path");
const fs = require('fs-extra')
const fetch = require('node-fetch');
const {Storage} = require('@google-cloud/storage');
const {getModifiedTime, decomposeGsUrl, downloadFolder} = require('./fileUtils');

storage = new Storage();

const REMOTE_TEMPLATES_PATH = "gs://kairos-motor.appspot.com/templates";
const LOCAL_TEMPLATES_DIR = path.resolve("templates");

/**
 * Prepares the render "environment" for a given request: downloads or copies
 * all the ressources needed for a render according to the request.
 * @param {renderRequest} request - the object that defines the request
 */
async function prepareRender (request, renderProjectDir, logger) {
  logger.info('prepare render');

  // Define some paths
  const templateSourceDir = path.join(LOCAL_TEMPLATES_DIR, request.template);
  
  // Ensure the template exists locally and is up to date
  await updateTemplate(request.template, logger);
  
  // Create the (tempoary) render project dir, and copy the template dir there
  await fs.mkdirp(renderProjectDir);
  await fs.copy(templateSourceDir, renderProjectDir);
  
  const promises = [];
  // get every resource in the render dir
  for (let ressourceItem of request.resources) {
    const filePath = path.join(renderProjectDir, ressourceItem.target);

    if ('data' in ressourceItem) {
      let data;
      if(typeof ressourceItem.data == 'object') {
        // Here, we need a trick to avoid after effects's usesless, yet
        // blocking popup: 'the structure of the data file has changed'.
        // New keys can't be added, even the order of the keys needs to
        // be respected.
        // For that, we load the data file that was saved with the
        // template (so it must have the expected 'structure') and
        // replace the values with the request's when they match.
        // This technique prevents unknown keys from being added and
        // also preserves the original order.
        // TODO: Make this more generic (eg. as-is, it
        // wouldn't work with downloaded ressouces)
        let templatecontent;
        let objectdata = {};
        if (await fs.exists(filePath)) {
          templatecontent = await fs.readFile(filePath);
          objectdata = JSON.parse(templatecontent.toString('utf8'));
        }
        for (let key in objectdata) {
          if (key in ressourceItem.data){
            objectdata[key] = ressourceItem.data[key];
          }
        }
        data = JSON.stringify(objectdata);
      } else if (typeof ressourceItem.data == 'string') {
        data = ressourceItem.data;
      }
      fs.outputFile(filePath, data);
    } else if ('src' in ressourceItem) {
      promises.push(fetchResource(ressourceItem.src, filePath));
    }
  }
  await Promise.all(promises);
}

async function fetchResource(urls, targetPath) {
  if(Array.isArray(urls)) {
    const promises = urls.map((url, idx)=>{
      let targetPathIndexed = targetPath.replace('#', idx);
      return fetchResource(url, targetPathIndexed)
    });
    return Promise.all(promises)
  }
  
  let url = urls;
  await fs.ensureFile(targetPath)

  if(url.startsWith("gs://")) {
    const {bucket, filepath} = decomposeGsUrl(url);

    await storage
      .bucket(bucket)
      .file(filepath)
      .download({destination:targetPath});
  } else {
    response = await fetch(url);
    if (response.status !== 200) {
      throw new Error('failed asset request: ' + url);
    } else {
      const file = fs.createWriteStream(targetPath);
      let promise = new Promise((resolve, reject)=>{
        response.body.pipe(file);
        response.body.on('end', resolve);
        response.body.on('error', reject);
      })
      await promise;
      file.close();
    }
  }
}

/**
 * Checks wether a local template is up to date. If not (of if it does not
 * exist), downloads it from storage.
 * @param {String} templateName Name of the template
 * @param {Loger} logger
 */
async function updateTemplate(templateName, logger=console) {
  // Compose the various paths we'll need
  template_dir = `${REMOTE_TEMPLATES_PATH}/${templateName}`;
  template_path = `${template_dir}/template.aep`;
  local_template_dir = `${LOCAL_TEMPLATES_DIR}/${templateName}`;
  local_template_path = `${local_template_dir}/template.aep`;

  const [local_mtime, remote_mtime] = await Promise.all([
    getModifiedTime(local_template_path),
    getModifiedTime(template_path),
  ]);

  if (remote_mtime === null) {
    throw new Error(`template '${templateName}' was not foud`);
  }

  if (local_mtime === null || local_mtime<remote_mtime) {
    logger.info(`updating template '${templateName}'`);
    await downloadFolder(template_dir, local_template_dir);
  } else {
    logger.info(`template '${templateName}' is up to date`);
  }
}

module.exports = prepareRender;