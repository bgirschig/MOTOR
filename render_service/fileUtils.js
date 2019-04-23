const path = require("path");
const fs = require('fs-extra')
const {Storage} = require('@google-cloud/storage');

// init cloud storage client
storage = new Storage();

/**
 * Returns the specified file's last modified date, or null if the file can't be
 * found. Supports local filesystem and gcloud storage urls
 * note: gcloud storage's "modified date" corresponds to the date of last upload
 *  not necessarily modification.
 * @param {String} path the path / uri to the file
 * @returns {Promise<Date|null>} The modified time of the file if it exists,
 *          null otherwise
 */
async function getModifiedTime(path) {
  if (path.startsWith('gs://')) {
    const {bucket, filepath} = decomposeGsUrl(path);
    try {
      const [metadata] = await storage
        .bucket(bucket)
        .file(filepath)
        .getMetadata();
      return new Date(metadata.timeStorageClassUpdated);
    } catch (e) {
      if (e.code === 404) {
        // file not found, return null
        return null;
      } else {
        // unexpected error
        throw e;
      }
    }
  } else {
    try {
      const stats = await fs.stat(path);
      return new Date(stats.mtime);
    } catch (e) {
      if (e.code === 'ENOENT') {
        // The file does not exist.
        return null;
      } else {
        throw e;
      }
    }
  }
};

/**
 * @typedef {Object} GSUrlParts
 * @property {string} bucket bucket name
 * @property {string} file file path within the bucket
 */

/**
 * Splits a gcloud storage uri into its 2 components: bucket name and file path
 * @param {String} url A gs uri to a file or directory: gs://bucketname/filepath
 * @returns {GSUrlParts}
 */
function decomposeGsUrl(url) {
  const parts = url.replace('gs://', '').split('/');
  const bucket = parts[0];
  const filepath = parts.slice(1).join('/');
  return {bucket, filepath};
}

async function downloadFolder(gsPath, target="./") {
  const {bucket, filepath} = decomposeGsUrl(gsPath);

  // get file list in folder
  const [files] = await storage
    .bucket(bucket)
    .getFiles({prefix: filepath});
  
  // download all files from list
  const promises = files.map(async file=>{
    const relative_filename = path.relative(filepath, file.name);
    const filename = path.join(target, relative_filename);
    await fs.ensureDir(path.dirname(filename));
    return file.download({destination:filename})
  });

  return Promise.all(promises);
}

/** Updates a file's 'modified time' to now */
async function touch(filepath) {
  const stats = await fs.stat(filepath);
  await fs.utimes(filepath, stats.atime, new Date());
}

/**
 * Returns all the files whose name mathes the given one, with any extension
 * (equivalent of <dir>/<name>.*)
 * @param {string} name The name of the file(s) to match, without extension
 */
async function findFiles(dir, name) {
  let files = await fs.readdir(dir);
  matched = files.filter(file => path.parse(file).name === name);
  matched = matched.map(file=>path.join(dir, file));
  return matched;
}

/** Counts the number of files in a directory */
async function cout_files(dir) {
  return fs.readdir(dir).then((files)=>{
    return files.length;
  })
}

module.exports = {
  getModifiedTime,
  decomposeGsUrl,
  downloadFolder,
  touch,
  findFiles,
  cout_files
};