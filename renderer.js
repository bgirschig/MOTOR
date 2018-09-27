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

async function handle_request(request) {
    console.log('[step] start')
    let {templateFilePath, outputDir, renderProjectDir} = await prepareRender(request);

    let losslessFile = path.join(outputDir, 'lossless');
    let compName = request.compName || DEFAULT_COMP_NAME;

    try {
        await render(templateFilePath, losslessFile, compName, renderProjectDir);
        
        // find the lossless file (after effects replaces the extension
        // depending on the environment, so we can't know)
        losslessFiles = await findFiles(outputDir, 'lossless');
        if (losslessFiles.length === 0) throw new Error('render file (lossless.*) not found');
        if (losslessFiles.length > 1) throw new Error('more than one render file (lossless.*) found');
        losslessFile = losslessFiles[0];

        await runEncoders(losslessFile, request.encoders);
        await fs.remove(losslessFile);
        await upload_renders(outputDir, request.id);
    } catch (err) {
        console.error('error:', err);
    }

    console.log('[step] cleanup');
    await fs.remove(renderProjectDir);

    console.log('[step] done');
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

async function upload_renders (outputDir, target) {
    console.log('[step] upload')
    const client = new ftp.Client();
    try {
        await client.access(config.ftp);
        console.log('[step][ftp] connected')
        await client.cd(REMOTE_OUTPUT_DIR);
        console.log('[step][ftp] cd\'d to dir')
        await client.uploadDir(outputDir, target);
        console.log('[step][ftp] uploaded')
    } catch(err) {
        console.log(err);
    }
    client.close();
}

function render (templateFilePath, losslessFile, compName) {
    console.log('[step] render')
    let args = [
        '-project', templateFilePath,
        '-comp', compName,
        '-output', losslessFile,
    ]
    console.log(config.ae_render, args.join(' '));

    var ae = spawn(config.ae_render, args);
    ae.stdin.end();
    ae.on('error', function (err) {
        console.log('error:', err);
    });
    ae.stdout.on('data', data => {
        console.log('stdout: ' + data.toString().trim());
    })
    ae.stderr.on('data', function (data) {
        console.log('stderr:', data.toString());
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
async function prepareRender (request) {
    console.log('[step] prepare render')

    let promises = [];

    // Define some paths
    const renderProjectDir = path.join(RENDER_TEMPS_DIR, request.id);
    const resourcesPath = path.join(renderProjectDir, "(Metrage)");
    const templateSourceDir = path.join(TEMPLATES_DIR, request.template);
    // no extension: aerender selects it depending on output module
    const outputDir = path.join(renderProjectDir, 'output');
    const templateFilePath = path.join(renderProjectDir, 'template.aepx');

    // Create folders
    promises.push(fs.ensureDir(RENDER_TEMPS_DIR));
    promises.push(fs.ensureDir(renderProjectDir));
    promises.push(fs.ensureDir(resourcesPath));
    promises.push(fs.ensureDir(outputDir));

    await Promise.all(promises);
    promises = [];

    // Copy template files
    await fs.copy(templateSourceDir, renderProjectDir);

    // get every resource in the render dir
    for (let ressourceItem of request.resources) {
        const filePath = path.join(resourcesPath, ressourceItem.target);
        const file = fs.createWriteStream(filePath);

        if ('data' in ressourceItem) {
            let data;
            if(typeof ressourceItem.data == 'object') {
                data = JSON.stringify(ressourceItem.data);
            } else if (typeof ressourceItem.data == 'string') {
                data = ressourceItem.data;
            }
            file.write(data);
            file.close();
        } else if ('source' in ressourceItem) {
            let resourcePromise = fetch(ressourceItem.source)
            .then(resp=>{
                return new Promise((resolve, reject)=>{
                    resp.body.pipe(file);
                    resp.body.on('end', resolve);
                    resp.body.on('error', reject);
                })
                .then(()=>file.close())
            })
            .catch(console.error);

            promises.push(resourcePromise);
        }
    }
    await Promise.all(promises);

    return {templateFilePath, outputDir, renderProjectDir}
}

module.exports = handle_request