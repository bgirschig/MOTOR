const path = require("path");
const fs = require('fs-extra')
const fetch = require('node-fetch');
const {Storage} = require('@google-cloud/storage');

storage = new Storage();

/**
 * Prepares the render "environment" for a given request: downloads or copies
 * all the ressources needed for a render according to the request.
 * @param {renderRequest} request - the object that defines the request
 */
async function prepareRender (request, renderProjectDir, tmp_dir, templates_dir,
    logger) {
  logger.info('prepare render');

  let promises = [];

  // Define some paths
  const templateSourceDir = path.join(templates_dir, request.template);
  // no extension: aerender selects it depending on output module
  const outputDir = path.join(renderProjectDir, 'output');

  // Create folders
  promises.push(fs.ensureDir(tmp_dir));
  promises.push(fs.ensureDir(renderProjectDir));
  promises.push(fs.ensureDir(outputDir));

  await Promise.all(promises);
  promises = [];

  // Copy template files
  await fs.copy(templateSourceDir, renderProjectDir);

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

  return outputDir;
}

async function fetchResource(urls, targetPath) {
  if(Array.isArray(urls)) {
    promises = urls.map((url, idx)=>{
      let targetPathIndexed = targetPath.replace('#', idx);
      return fetchResource(url, targetPathIndexed)
    });
    return Promise.all(promises)
  }
  
  let url = urls;
  await fs.ensureFile(targetPath)

  if(url.startsWith("gs://")) {
    const parts = url.replace('gs://', '').split('/');
    const bucket = parts[0];
    const file = parts.slice(1).join('/');

    await storage
      .bucket(bucket)
      .file(file)
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

module.exports = prepareRender;