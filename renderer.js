// TODO: a more sensible approach to error handling: don't try to encode if
// render failed, don't try to upload if encode failed, etc...

const path = require("path");
const fs = require('fs-extra')
const fetch = require('node-fetch');
const ftp = require('basic-ftp');
const spawn = require('child_process').spawn;
const runEncoders = require('./encodersRunner');
const config = require("./config");

const RENDER_TEMPS_DIR = path.resolve('./render_tmps');
const TEMPLATES_DIR = path.resolve('./templates');
const DEFAULT_COMP_NAME = 'main';
const REMOTE_OUTPUT_DIR = 'render_outputs'

const isWin = process.platform === "win32";
const aerender = isWin ? config.ae_render : config.ae_render_osx;

async function handle_request(request, logger) {
    let {templateFilePath, outputDir, renderProjectDir} = await prepareRender(request, logger);
    let losslessFile = path.join(outputDir, 'lossless');
    let compName = request.compName || DEFAULT_COMP_NAME;

    try {
        await render(templateFilePath, losslessFile, compName, logger);
        logger.info('render successful');
        
        // find the lossless file (after effects replaces the extension
        // depending on the environment, so we can't know)
        losslessFiles = await findFiles(outputDir, 'lossless');
        if (losslessFiles.length === 0) throw new Error('rendered file not found');
        if (losslessFiles.length > 1) throw new Error('more than one rendered file found');
        losslessFile = losslessFiles[0];

        await runEncoders(losslessFile, request.encoders, logger);
        await fs.remove(losslessFile);
        await upload_renders(outputDir, request.id, logger);
    } catch (err) {
        logger.error(err);
    }

    await fs.remove(renderProjectDir);

    logger.info('done');
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

async function upload_renders (outputDir, target, logger) {
    const client = new ftp.Client();
    try {
        await client.access(config.ftp);
        await client.cd(REMOTE_OUTPUT_DIR);
        await client.uploadDir(outputDir, target);
        logger.info('upload successful');
    } catch(err) {
        logger.error(err, 'upload failed');
    }
    client.close();
}

function render (templateFilePath, losslessFile, compName, logger) {
    let args = [
        '-project', templateFilePath,
        '-comp', compName,
        '-output', losslessFile,
        '-continueOnMissingFootage',
    ];

    logger.info({
        command:{
            'command-path': aerender,
            'args': args,
        }
    }, `spawn process: ${aerender + args.join(' ')}`);

    // TODO: add a timeout
    // TODO: bundle multiple stdout lines together before sending, or only
    // debug-log them
    var ae = spawn(aerender, args);
    ae.stdin.end();
    ae.on('error', function (err) {
        logger.error(err, String(err));
    });
    ae.stdout.on('data', data => {
        logger.info('stdout: ' + data.toString().trim());
    })
    ae.stderr.on('data', function (data) {
        logger.error('stderr:', data.toString());
    });
    return new Promise((resolve, reject)=>{
        ae.on('close', function (code) {
            if (code == 0) resolve();
            else reject('aerender command failed');
        });
    })
}

/**
 * Prepares the render "environment" for a given request: downloads or copies
 * all the ressources needed for a render according to the request.
 * @param {renderRequest} request - the object that defines the request
 */
async function prepareRender (request, logger) {
    logger.info('prepare render');

    let promises = [];

    // Define some paths
    const renderProjectDir = path.join(RENDER_TEMPS_DIR, request.id);
    const templateSourceDir = path.join(TEMPLATES_DIR, request.template);
    // no extension: aerender selects it depending on output module
    const outputDir = path.join(renderProjectDir, 'output');
    const templateFilePath = path.join(renderProjectDir, 'template.aep');

    // Create folders
    promises.push(fs.ensureDir(RENDER_TEMPS_DIR));
    promises.push(fs.ensureDir(renderProjectDir));
    promises.push(fs.ensureDir(outputDir));

    await Promise.all(promises);
    promises = [];

    // Copy template files
    await fs.copy(templateSourceDir, renderProjectDir);

    // get every resource in the render dir
    for (let ressourceItem of request.resources) {
        const filePath = path.join(renderProjectDir, ressourceItem.target);
        
        // Read the current template content, before creating the write stream
        let templatecontent = '';

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
                for (key in objectdata) {
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

    return {templateFilePath, outputDir, renderProjectDir}
}

async function fetchResource(urls, targetPath) {
    if(Array.isArray(urls)) {
        promises = urls.map((url, idx)=>{
            let targetPathIndexed = targetPath.replace('#', idx);
            return fetchResource(url, targetPathIndexed)
        });
        return Promise.all(promises)
    } else {
        let url = urls;

        await fs.ensureFile(targetPath)
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
            await promise
            file.close()
        }
    }
}

module.exports = handle_request